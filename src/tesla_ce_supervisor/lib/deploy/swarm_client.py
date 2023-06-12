import docker
from docker.types.healthcheck import Healthcheck
from docker.types.services import EndpointSpec, SecretReference, ConfigReference
import base64
import os
import typing
import yaml
import tempfile
import json

from django.template.loader import render_to_string
from django.conf import settings
from yaml.loader import SafeLoader


from .base import BaseDeploy
from ..models.check import ServiceDeploymentInformation, ConnectionStatus, CommandStatus
from ..setup_options import SetupOptions
from ..tesla.conf import Config
from ..tesla.modules import get_modules
from .exceptions import TeslaDeployException


class SwarmDeploy(BaseDeploy):
    _client = None

    def __init__(self, config: typing.Optional[Config] = None) -> None:
        super().__init__(config)
        self.config = config

    @property
    def client(self):
        if self._client is None:
            self.config.get('swarm_base_url')

            tls_config = None

            if self.config.get('swarm_client_key') is not None and self.config.get('swarm_client_cert') is not None and \
                    self.config.get('swarm_specific_ca_cert') is not None:

                client_key_file = os.path.join(settings.DATA_DIRECTORY, 'client_key.pem')
                with open(client_key_file, 'w') as file:
                    content = base64.b64decode(self.config.get('swarm_client_key')).decode('utf8')
                    file.write(content)
                    file.close()

                client_cert_file = os.path.join(settings.DATA_DIRECTORY, 'client_cert.pem')
                with open(client_cert_file, 'w') as file:
                    content = base64.b64decode(self.config.get('swarm_client_cert')).decode('utf8')
                    file.write(content)
                    file.close()

                client_ca_file = os.path.join(settings.DATA_DIRECTORY, 'client_ca.pem')
                with open(client_ca_file, 'w') as file:
                    content = base64.b64decode(self.config.get('swarm_specific_ca_cert')).decode('utf8')
                    file.write(content)
                    file.close()

                tls_config = docker.tls.TLSConfig(
                    client_cert=(client_cert_file, client_key_file), ca_cert=client_ca_file
                )

            self._client = docker.DockerClient(base_url=self.config.get('swarm_base_url'), tls=tls_config)

        assert self._client is not None

        return self._client

    def _create_status_obj(self, name: str) -> ServiceDeploymentInformation:
        # Check if job exists
        '''
        job_info = None
        if len(self.client.jobs.get_jobs(name)) == 1:
            job_info = self.client.job.get_deployment(name)
        '''
        service_id = '{}_{}'.format(self.config.get('SWARM_SERVICE_PREFIX'), name)
        status = ServiceDeploymentInformation(service_id, 'swarm', {})

        try:
            service = self.client.services.get(service_id)
            total_instances = service.attrs['Spec']['Mode']['Replicated']['Replicas']
            healthy_instances = len(service.tasks(filters={'desired-state': 'RUNNING'}))
            preparing_instances = len(service.tasks(filters={'desired-state': 'PREPARING'})) + \
                                  len(service.tasks(filters={'desired-state': 'STARTING'}))
            status.jobs_running = healthy_instances
            status.jobs_expected = total_instances
            status.jobs_healthy = healthy_instances

            if status.jobs_healthy == status.jobs_expected:
                status.status = 'success'
            elif preparing_instances > 0:
                status.status = 'waiting'
            else:
                status.status = 'error'

        except docker.errors.NotFound:
            pass

        return status

    def _remove_swarm_service(self, name: str, template: str, context: dict = {}) -> dict:
        service_id = '{}_{}'.format(self.config.get('SWARM_SERVICE_PREFIX'), name)
        try:
            service = self.client.services.get(service_id)
            service.remove()

            # remove secrets
            task_def = self._remove_empty_lines(render_to_string(template, context))

            task_def_dict = yaml.load(task_def, Loader=SafeLoader)
            service_def_dict = task_def_dict['services'][name]
            if 'secrets' in service_def_dict:
                for sec in service_def_dict['secrets']:
                    try:
                        secret_id = sec.upper()
                        secret = self.client.secrets.get(secret_id)
                        secret.remove()
                    except docker.errors.DockerException:
                        pass

        except docker.errors.DockerException:
            pass

        return {}

    def _create_swarm_service(self, name: str, template: str, context: dict) -> dict:
        task_def = self._remove_empty_lines(render_to_string(template, context))

        task_def_dict = yaml.load(task_def, Loader=SafeLoader)
        service_def_dict = task_def_dict['services'][name]
        service_def_dict['name'] = '{}_{}'.format(self.config.get('SWARM_SERVICE_PREFIX'), name)

        image = service_def_dict['image']
        del service_def_dict['image']

        command = None
        if 'command' in service_def_dict:
            command = service_def_dict['command']
            del service_def_dict['command']
            service_def_dict['args'] = command

            if type(service_def_dict['args']) == str:
                service_def_dict['args'] = [service_def_dict['args']]

        command = None
        if 'entrypoint' in service_def_dict:
            command = service_def_dict['entrypoint']
            del service_def_dict['entrypoint']

        # contraints, rrestart policy, etc...
        for key in service_def_dict['deploy'].keys():
            if key == 'placement':
                for subkey in service_def_dict['deploy'][key].keys():
                    service_def_dict[subkey] = service_def_dict['deploy'][key][subkey]
            elif key == 'labels':
                labels = {}
                for item in service_def_dict['deploy'][key]:
                    labels[item.split('=')[0]] = item.split('=')[1]

                service_def_dict[key] = labels
            elif key != 'replicas':
                service_def_dict[key] = service_def_dict['deploy'][key]

        del service_def_dict['deploy']

        # ports
        endpoint_spec = None
        if 'ports' in service_def_dict:
            res_ports = []
            for port in service_def_dict['ports']:
                aux = {
                    'TargetPort': int(port.split(':')[1]),
                    'PublishedPort': int(port.split(':')[0])
                }
                res_ports.append(aux)

            service_def_dict['endpoint_spec'] = EndpointSpec(ports=res_ports)

            del service_def_dict['ports']


        # check if all networks are created:
        networks_rename = []
        for net in service_def_dict['networks']:
            try:
                network_id = '{}_{}'.format(self.config.get('SWARM_SERVICE_PREFIX'), net)
                network = self.client.networks.get(network_id)
                # in this case netowrk exists
                networks_rename.append(network_id)
            except docker.errors.NotFound:
                self.client.networks.create(name=network_id, driver='overlay', attachable=True)
                networks_rename.append(network_id)
            except docker.errors.DockerException:
                pass

        service_def_dict['networks'] = networks_rename

        # check volumes
        if 'volumes' in task_def_dict and task_def_dict['volumes'] is not None:
            for vol in task_def_dict['volumes']:
                try:
                    volume_id = vol
                    volume = self.client.volumes.get(volume_id)
                except docker.errors.NotFound:
                    driver_opts = task_def_dict['volumes'][vol]['driver_opts']
                    self.client.volumes.create(name=volume_id, driver='local', driver_opts=driver_opts)
                except docker.errors.DockerException:
                    pass

            service_def_dict['mounts'] = service_def_dict['volumes']

        if 'volumes' in task_def_dict:
            del service_def_dict['volumes']

        # environment
        if 'environment' in service_def_dict:
            service_def_dict['env'] = service_def_dict['environment']
            del service_def_dict['environment']

        # create secrets
        secrets_rename = []

        if 'secrets' in service_def_dict:
            for sec in service_def_dict['secrets']:
                secret_id = sec.upper()
                try:
                    secret = self.client.secrets.get(secret_id)
                    secrets_rename.append(SecretReference(secret_id=secret.attrs['ID'],
                                                          secret_name=secret.name))
                except docker.errors.NotFound:
                    secret_data = context[sec]
                    secret = self.client.secrets.create(name=secret_id, data=secret_data)
                    secrets_rename.append(SecretReference(secret_id=secret.attrs['ID'],
                                                          secret_name=secret.name))
                except docker.errors.DockerException:
                    pass

            service_def_dict['secrets'] = secrets_rename

        # healthcheck
        if 'healthcheck' in service_def_dict:
            start_period = 1000000
            if 'start_period' in service_def_dict['healthcheck']:
                start_period = int(service_def_dict['healthcheck']['start_period'][:-1])*1000000000
            service_def_dict['healthcheck'] = Healthcheck(test=service_def_dict['healthcheck']['test'],
                                                          interval=int(service_def_dict['healthcheck']['interval'][:-1])*1000000000,
                                                          timeout=int(service_def_dict['healthcheck']['timeout'][:-1])*1000000000,
                                                          retries=service_def_dict['healthcheck']['retries'],
                                                          start_period=start_period)
        #config file

        if 'configs' in task_def_dict:
            configs_rename = []
            configs_aux = {}
            for key in task_def_dict['configs']:
                file = task_def_dict['configs'][key]['file']

                try:
                    config_id = "{}_{}".format(self.config.get('SWARM_SERVICE_PREFIX'), key)
                    config = self.client.configs.get(config_id)
                    configs_aux[key] = config
                except docker.errors.NotFound as err:
                    config_id = "{}_{}".format(self.config.get('SWARM_SERVICE_PREFIX'), key)

                    template = 'services/{}/swarm/{}'.format(name, file)
                    config_data = render_to_string(template, context)
                    config_data = render_to_string(template, context)
                    self.client.configs.create(name=config_id, data=config_data)
                    config = self.client.configs.get(config_id)
                    configs_aux[key] = config
                except docker.errors.DockerException as err:
                    pass

            for key in service_def_dict['configs']:
                for key2 in configs_aux.keys():
                    if key2 == key['source']:
                        c = configs_aux[key2]
                        configs_rename.append(ConfigReference(config_id=c.id, config_name=c.name, filename=key['target']))

            service_def_dict['configs'] = configs_rename

        if os.getenv('ADD_HOSTS', '') != '':
            service_def_dict['hosts'] = json.loads(os.getenv('ADD_HOSTS', ''))

        try:
            self.client.images.pull(image)
            self.client.services.create(image=image, command=command, **service_def_dict)
        except docker.errors.DockerException as err:
            print(err)
            pass
        return {}

    def write_scripts(self) -> None:
        """
            Write deployment scripts
        """
        pass

    def _deploy_lb(self) -> dict:
        """
            Deploy Load Balancer
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_ADMIN_MAIL': self._config.get('TESLA_ADMIN_MAIL'),
            'DEBUG': settings.DEBUG,
        }

        return self._create_swarm_service('traefik', 'lb/traefik/swarm/traefik.yaml', context)

    def _get_lb_script(self) -> SetupOptions:
        """
            Get the script to deploy Load Balancer
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_ADMIN_MAIL': self._config.get('TESLA_ADMIN_MAIL')
        }

        task_def = self._remove_empty_lines(render_to_string('lb/traefik/swarm/traefik.yaml', context))

        script = SetupOptions()

        script.add_command(
            command='docker network create --driver overlay tesla_public',
            description='Create if not exists tesla_public network'
        )
        script.add_command(
            command='docker network create --driver overlay tesla_private',
            description='Create if not exists tesla_private network'
        )
        script.add_command(
            command='docker stack -t traefik.yaml tesla',
            description='Create new service for Traefik Load Balancer'
        )

        script.add_file(
            filename='traefik.yaml',
            description='Stack description for Traefik Load Balancer',
            content=task_def,
            mimetype='application/yaml'
        )

        return script

    def _get_lb_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for Load Balancer
        """
        return self._create_status_obj('traefik')

    def _deploy_vault(self) -> dict:
        """
            Deploy Hashicorp Vault
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'VAULT_BACKEND': self._config.get('VAULT_BACKEND'),
            'VAULT_DB_HOST': self._config.get('VAULT_DB_HOST'),
            'VAULT_DB_PORT': self._config.get('VAULT_DB_PORT'),
            'VAULT_DB_USER': self._config.get('VAULT_DB_USER'),
            'VAULT_DB_PASSWORD': self._config.get('VAULT_DB_PASSWORD'),
            'VAULT_DB_NAME': self._config.get('VAULT_DB_NAME'),
            'DB_PASSWORD': self._config.get('DB_PASSWORD'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB')
        }

        return self._create_swarm_service('vault', 'services/vault/swarm/vault.yaml', context)

    def _get_vault_script(self) -> SetupOptions:
        """
            Get the script to deploy Hashicorp Vault
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'VAULT_BACKEND': self._config.get('VAULT_BACKEND'),
            'VAULT_DB_HOST': self._config.get('VAULT_DB_HOST'),
            'VAULT_DB_PORT': self._config.get('VAULT_DB_PORT'),
            'VAULT_DB_USER': self._config.get('VAULT_DB_USER'),
            'VAULT_DB_PASSWORD': self._config.get('VAULT_DB_PASSWORD'),
            'VAULT_DB_NAME': self._config.get('VAULT_DB_NAME'),
            'DB_PASSWORD': self._config.get('DB_PASSWORD'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB')
        }

        task_def = self._remove_empty_lines(render_to_string('services/vault/swarm/vault.yaml', context))
        secret_VAULT_DB_PASSWORD = ''
        if self._config.get('VAULT_DB_PASSWORD') is not None:
            secret_VAULT_DB_PASSWORD = self._config.get('VAULT_DB_PASSWORD')

        secret_DB_PASSWORD = ''
        if self._config.get('DB_PASSWORD') is not None:
            secret_DB_PASSWORD = self._config.get('DB_PASSWORD')

        script = SetupOptions()
        script.add_command(
            command='docker stack -t vault.yaml tesla',
            description='Create new service for vault'
        )

        script.add_file(
            filename='vault.yaml',
            description='Stack description for vault',
            content=task_def,
            mimetype='application/yaml'
        )

        script.add_file(
            filename='secrets/VAULT_DB_PASSWORD',
            description='Secret VAULT_DB_PASSWORD',
            content=secret_VAULT_DB_PASSWORD,
            mimetype='text/plain'
        )

        script.add_file(
            filename='secrets/DB_PASSWORD',
            description='Secret DB_PASSWORD',
            content=secret_DB_PASSWORD,
            mimetype='text/plain'
        )

        return script

    def _deploy_minio(self) -> dict:
        """
            Deploy MinIO
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'STORAGE_REGION': self._config.get('STORAGE_REGION'),
            'STORAGE_ACCESS_KEY': self._config.get('STORAGE_ACCESS_KEY'),
            'STORAGE_SECRET_KEY': self._config.get('STORAGE_SECRET_KEY'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB')
        }

        return self._create_swarm_service('minio', 'services/minio/swarm/minio.yaml', context)

    def _get_minio_script(self) -> SetupOptions:
        """
            Get the script to deploy MinIO
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'STORAGE_REGION': self._config.get('STORAGE_REGION'),
            'STORAGE_ACCESS_KEY': self._config.get('STORAGE_ACCESS_KEY'),
            'STORAGE_SECRET_KEY': self._config.get('STORAGE_SECRET_KEY'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB')
        }

        task_def = self._remove_empty_lines(render_to_string('services/minio/swarm/minio.yaml', context))
        secret_STORAGE_ACCESS_KEY = ''
        if self._config.get('STORAGE_ACCESS_KEY') is not None:
            secret_STORAGE_ACCESS_KEY = self._config.get('STORAGE_ACCESS_KEY')

        secret_STORAGE_SECRET_KEY = ''
        if self._config.get('STORAGE_SECRET_KEY') is not None:
            secret_STORAGE_SECRET_KEY = self._config.get('STORAGE_SECRET_KEY')

        script = SetupOptions()
        script.add_command(
            command='docker stack -t minio.yaml tesla',
            description='Create new service for MinIO'
        )

        script.add_file(
            filename='minio.yaml',
            description='Stack description for MinIO',
            content=task_def,
            mimetype='application/yaml'
        )

        script.add_file(
            filename='secrets/STORAGE_ACCESS_KEY',
            description='Secret STORAGE_ACCESS_KEY',
            content=secret_STORAGE_ACCESS_KEY,
            mimetype='text/plain'
        )

        script.add_file(
            filename='secrets/STORAGE_SECRET_KEY',
            description='Secret STORAGE_SECRET_KEY',
            content=secret_STORAGE_SECRET_KEY,
            mimetype='text/plain'
        )

        return script

    def _deploy_redis(self) -> dict:
        """
            Deploy Redis
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'REDIS_PASSWORD': self._config.get('REDIS_PASSWORD'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB')
        }

        return self._create_swarm_service('redis', 'services/redis/swarm/redis.yaml', context)

    def _get_redis_script(self) -> SetupOptions:
        """
            Get the script to deploy Redis
        """
        script = SetupOptions()

        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'REDIS_PASSWORD': self._config.get('REDIS_PASSWORD'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB')
        }

        task_def = self._remove_empty_lines(render_to_string('services/redis/swarm/redis.yaml', context))
        secret_REDIS_PASSWORD = ''
        if self._config.get('REDIS_PASSWORD') is not None:
            secret_REDIS_PASSWORD = self._config.get('REDIS_PASSWORD')

        script = SetupOptions()
        script.add_command(
            command='docker stack -t redis.yaml tesla',
            description='Create new service for redis'
        )

        script.add_file(
            filename='redis.yaml',
            description='Stack description for Redis',
            content=task_def,
            mimetype='application/yaml'
        )

        script.add_file(
            filename='secrets/REDIS_PASSWORD',
            description='Secret REDIS_PASSWORD',
            content=secret_REDIS_PASSWORD,
            mimetype='text/plain'
        )

        return script

    def _deploy_database(self) -> dict:
        """
            Deploy Database
        """
        if self._config.get('DB_ENGINE') == 'mysql':
            db_image = 'mariadb'
            name = 'mysql'
            template = 'services/database/mysql/swarm/mysql.yaml'
        elif self._config.get('DB_ENGINE') == 'postgresql':
            db_image = None
            name = None
            template = None
        else:
            db_image = None
            name = None
            template = None

        if db_image is None:
            raise TeslaDeployException('Invalid database engine')

        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'DB_ROOT_PASSWORD': self._config.get('DB_ROOT_PASSWORD'),
            'DB_PASSWORD': self._config.get('DB_PASSWORD'),
            'DB_USER': self._config.get('DB_USER'),
            'DB_NAME': self._config.get('DB_NAME'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB')
        }

        return self._create_swarm_service('database', template, context)

    def _get_database_script(self) -> SetupOptions:
        """
            Get the script to deploy Database
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'DB_ROOT_PASSWORD': self._config.get('DB_ROOT_PASSWORD'),
            'DB_PASSWORD': self._config.get('DB_PASSWORD'),
            'DB_USER': self._config.get('DB_USER'),
            'DB_NAME': self._config.get('DB_NAME'),
            'VAULT_DB_PASSWORD': self._config.get('VAULT_DB_PASSWORD'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB')
        }
        task_def = self._remove_empty_lines(render_to_string('services/database/mysql/swarm/mysql.yaml', context))
        secret_DB_ROOT_PASSWORD = ''
        if self._config.get('DB_ROOT_PASSWORD') is not None:
            secret_DB_ROOT_PASSWORD = self._config.get('DB_ROOT_PASSWORD')

        secret_DB_PASSWORD = ''
        if self._config.get('DB_PASSWORD') is not None:
            secret_DB_PASSWORD = self._config.get('DB_PASSWORD')

        secret_VAULT_DB_PASSWORD = ''
        if self._config.get('VAULT_DB_PASSWORD') is not None:
            secret_DB_PASSWORD = self._config.get('VAULT_DB_PASSWORD')

        script = SetupOptions()
        script.add_command(
            command='docker stack -t database.yaml tesla',
            description='Create new service for database'
        )

        script.add_file(
            filename='database.yaml',
            description='Stack description for Database',
            content=task_def,
            mimetype='application/yaml'
        )

        script.add_file(
            filename='secrets/DB_ROOT_PASSWORD',
            description='Secret DB_ROOT_PASSWORD',
            content=secret_DB_ROOT_PASSWORD,
            mimetype='text/plain'
        )
        script.add_file(
            filename='secrets/DB_PASSWORD',
            description='Secret DB_PASSWORD',
            content=secret_DB_PASSWORD,
            mimetype='text/plain'
        )
        script.add_file(
            filename='secrets/VAULT_DB_PASSWORD',
            description='Secret VAULT_DB_PASSWORD',
            content=secret_VAULT_DB_PASSWORD,
            mimetype='text/plain'
        )

        return script

    def _deploy_rabbitmq(self) -> dict:
        """
           Deploy RabbitMQ
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'RABBITMQ_ADMIN_USER': self._config.get('RABBITMQ_ADMIN_USER'),
            'RABBITMQ_ADMIN_PASSWORD': self._config.get('RABBITMQ_ADMIN_PASSWORD'),
            'RABBITMQ_ERLANG_COOKIE': self._config.get('RABBITMQ_ERLANG_COOKIE'),
            'RABBITMQ_ADMIN_PORT': self._config.get('RABBITMQ_ADMIN_PORT'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB')
        }

        return self._create_swarm_service('rabbitmq', 'services/rabbitmq/swarm/rabbitmq.yaml', context)

    def _get_rabbitmq_script(self) -> SetupOptions:
        """
            Get the script to deploy RabbitMQ
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'RABBITMQ_ADMIN_USER': self._config.get('RABBITMQ_ADMIN_USER'),
            'RABBITMQ_ADMIN_PASSWORD': self._config.get('RABBITMQ_ADMIN_PASSWORD'),
            'RABBITMQ_ERLANG_COOKIE': self._config.get('RABBITMQ_ERLANG_COOKIE'),
            'RABBITMQ_ADMIN_PORT': self._config.get('RABBITMQ_ADMIN_PORT'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB')
        }

        task_def = self._remove_empty_lines(render_to_string('services/rabbitmq/swarm/rabbitmq.yaml', context))
        secret_RABBITMQ_ADMIN_USER = ''
        if self._config.get('RABBITMQ_ADMIN_USER') is not None:
            secret_RABBITMQ_ADMIN_USER = self._config.get('RABBITMQ_ADMIN_USER')

        secret_RABBITMQ_ADMIN_PASSWORD = ''
        if self._config.get('RABBITMQ_ADMIN_PASSWORD') is not None:
            secret_RABBITMQ_ADMIN_PASSWORD = self._config.get('RABBITMQ_ADMIN_PASSWORD')

        secret_RABBITMQ_ERLANG_COOKIE = ''
        if self._config.get('RABBITMQ_ERLANG_COOKIE') is not None:
            secret_RABBITMQ_ERLANG_COOKIE = self._config.get('RABBITMQ_ERLANG_COOKIE')

        script = SetupOptions()
        script.add_command(
            command='docker stack -t rabbitmq.yaml tesla',
            description='Create new service for rabbitmq'
        )

        script.add_file(
            filename='rabbitmq.yaml',
            description='Stack description for rabbitmq',
            content=task_def,
            mimetype='application/yaml'
        )

        script.add_file(
            filename='secrets/RABBITMQ_ADMIN_USER',
            description='Secret RABBITMQ_ADMIN_USER',
            content=secret_RABBITMQ_ADMIN_USER,
            mimetype='text/plain'
        )

        script.add_file(
            filename='secrets/RABBITMQ_ADMIN_PASSWORD',
            description='Secret RABBITMQ_ADMIN_PASSWORD',
            content=secret_RABBITMQ_ADMIN_PASSWORD,
            mimetype='text/plain'
        )

        script.add_file(
            filename='secrets/RABBITMQ_ERLANG_COOKIE',
            description='Secret RABBITMQ_ERLANG_COOKIE',
            content=secret_RABBITMQ_ERLANG_COOKIE,
            mimetype='text/plain'
        )

        return script

    def _remove_lb(self) -> dict:
        return self._remove_swarm_service('traefik', 'lb/traefik/swarm/traefik.yaml')

    def _remove_vault(self) -> dict:
        return self._remove_swarm_service('vault', 'services/vault/swarm/vault.yaml')

    def _get_vault_status(self) -> ServiceDeploymentInformation:
        return self._create_status_obj('vault')

    def _remove_minio(self) -> dict:
        return self._remove_swarm_service('minio', 'services/minio/swarm/minio.yaml')

    def _get_minio_status(self) -> ServiceDeploymentInformation:
        return self._create_status_obj('minio')

    def _remove_redis(self) -> dict:
        return self._remove_swarm_service('redis', 'services/redis/swarm/redis.yaml')

    def _get_redis_status(self) -> ServiceDeploymentInformation:
        return self._create_status_obj('redis')

    def _remove_database(self) -> dict:
        return self._remove_swarm_service('database', 'services/database/mysql/swarm/mysql.yaml')

    def _get_database_status(self) -> ServiceDeploymentInformation:
        return self._create_status_obj('database')

    def _remove_rabbitmq(self) -> dict:
        return self._remove_swarm_service('rabbitmq', 'services/rabbitmq/swarm/rabbitmq.yaml')

    def _get_rabbitmq_status(self) -> ServiceDeploymentInformation:
        return self._create_status_obj('rabbitmq')

    def test_connection(self) -> ConnectionStatus:
        pass

    def _deploy_supervisor(self) -> dict:
        """
           Deploy Supervisor
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'SUPERVISOR_SECRET': self._config.get('SUPERVISOR_SECRET'),
            'SUPERVISOR_ADMIN_USER': self._config.get('SUPERVISOR_ADMIN_USER'),
            'SUPERVISOR_ADMIN_PASSWORD': self._config.get('SUPERVISOR_ADMIN_PASSWORD'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB'),
            'SUPERVISOR_ADMIN_EMAIL': self._config.get('SUPERVISOR_ADMIN_EMAIL'),
        }

        return self._create_swarm_service('supervisor', 'supervisor/swarm/supervisor.yaml', context)

    def _remove_supervisor(self) -> dict:
        return self._remove_swarm_service('supervisor', 'supervisor/swarm/supervisor.yaml')

    def _get_supervisor_script(self) -> SetupOptions:
        """
            Get the script to deploy Supervisor
        """
        script = SetupOptions()

        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'SUPERVISOR_SECRET': self._config.get('SUPERVISOR_SECRET'),
            'SUPERVISOR_ADMIN_USER': self._config.get('SUPERVISOR_ADMIN_USER'),
            'SUPERVISOR_ADMIN_PASSWORD': self._config.get('SUPERVISOR_ADMIN_PASSWORD'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB')
        }

        task_def = self._remove_empty_lines(render_to_string('supervisor/swarm/supervisor.yaml', context))
        secret_SUPERVISOR_SECRET = ''
        if self._config.get('SUPERVISOR_SECRET') is not None:
            secret_SUPERVISOR_SECRET = self._config.get('SUPERVISOR_SECRET')

        secret_SUPERVISOR_ADMIN_USER = ''
        if self._config.get('SUPERVISOR_ADMIN_USER') is not None:
            secret_SUPERVISOR_ADMIN_USER = self._config.get('SUPERVISOR_ADMIN_USER')

        secret_SUPERVISOR_ADMIN_PASSWORD = ''
        if self._config.get('SUPERVISOR_ADMIN_PASSWORD') is not None:
            secret_SUPERVISOR_ADMIN_PASSWORD = self._config.get('SUPERVISOR_ADMIN_PASSWORD')

        script = SetupOptions()
        script.add_command(
            command='docker stack -t supervisor.yaml tesla',
            description='Create new service for supervisor'
        )

        script.add_file(
            filename='supervisor.yaml',
            description='Stack description for Supervisor',
            content=task_def,
            mimetype='application/yaml'
        )

        script.add_file(
            filename='secrets/SUPERVISOR_SECRET',
            description='Secret SUPERVISOR_SECRET',
            content=secret_SUPERVISOR_SECRET,
            mimetype='text/plain'
        )

        script.add_file(
            filename='secrets/SUPERVISOR_ADMIN_USER',
            description='Secret SUPERVISOR_ADMIN_USER',
            content=secret_SUPERVISOR_ADMIN_USER,
            mimetype='text/plain'
        )

        script.add_file(
            filename='secrets/SUPERVISOR_ADMIN_PASSWORD',
            description='Secret SUPERVISOR_ADMIN_PASSWORD',
            content=secret_SUPERVISOR_ADMIN_PASSWORD,
            mimetype='text/plain'
        )

        return script

    def _get_supervisor_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for TeSLA CE Supervisor
        """
        return self._create_status_obj('supervisor')

    def test_deployer(self):
        result = False
        info = ''
        try:
            self.client.version()
            result = True
        except docker.errors.DockerException as err:
            info = str(err)

        return {"result": result, "info": info}

    def execute_command_inside_container(self, image: str, command: str, environment: dict=None, timeout: int = 120) -> CommandStatus:
        """
            Execute command inside container
        """
        networks = []
        extra_hosts = {}
        auto_remove = False

        # image = 'teslace/core:local'
        environment['DJANGO_SETTINGS_MODULE'] = 'tesla_ce.settings'
        environment['DJANGO_CONFIGURATION'] = 'Setup'
        environment['SETUP_MODE'] = 'SETUP'

        networks = ['{}_tesla_private'.format(self.config.get('SWARM_SERVICE_PREFIX')),
                    '{}_tesla_public'.format(self.config.get('SWARM_SERVICE_PREFIX'))
                    ]

        if os.getenv('ADD_HOSTS', '') != '':
            extra_hosts = json.loads(os.getenv('ADD_HOSTS', ''))

        try:
            # first pull image
            self.client.images.pull(image)

            container = self.client.containers.create(image, command=command, environment=environment,
                                                      auto_remove=auto_remove, extra_hosts=extra_hosts)

            for net in networks:
                network = self.client.networks.get(net)
                network.connect(container)

            container.start()
            result = container.wait()

            status = True
            if 'StatusCode' in result and result['StatusCode'] != 0:
                status = False

            return CommandStatus(command=command, status=status, info={})
        except docker.errors.ContainerError as err:
            return CommandStatus(command=command, status=False, info=str(err))

    def _deploy_dashboard(self) -> dict:
        """
           Deploy API
        """
        context = {
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'DEPLOYMENT_VERSION': self._config.get('DEPLOYMENT_VERSION'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB'),
        }

        return self._create_swarm_service('dashboard', 'core/dashboard/swarm/dashboard.yaml', context)

    def _get_dashboard_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for TeSLA CE LAPI
        """
        return self._create_status_obj('dashboard')

    def _remove_dashboard(self) -> dict:
        context = {
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'DEPLOYMENT_VERSION': self._config.get('DEPLOYMENT_VERSION'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB'),
        }

        return self._remove_swarm_service('dashboard', 'core/dashboard/swarm/dashboard.yaml', context)

    def _get_dashboard_script(self) -> dict:
        """
           Deploy Dashboard
        """
        context = {
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'DEPLOYMENT_VERSION': self._config.get('DEPLOYMENT_VERSION'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB'),
        }

        task_def = self._remove_empty_lines(render_to_string('core/dashboard/swarm/dashboard.yaml', context))

        script = SetupOptions()
        script.add_command(
            command='docker stack -t tesla_dashboard.yaml tesla',
            description='Create tesla dashboard'
        )

        script.add_file(
            filename='tesla_dashboard.yaml',
            description='Stack description for tesla dashboard',
            content=task_def,
            mimetype='application/yaml'
        )

        return script

    def _deploy_core_module(self, credentials, deploy_module) -> dict:
        """
           Deploy API
        """
        context = {
            'DEPLOYMENT_SECRETS_PATH': self._config.get('DEPLOYMENT_SECRETS_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'DEPLOYMENT_IMAGE': self._config.get('DEPLOYMENT_IMAGE'),
            'DEPLOYMENT_VERSION': self._config.get('DEPLOYMENT_VERSION'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB'),
            'VAULT_URL': self._config.get('VAULT_URL'),
            'VAULT_MOUNT_PATH_KV': self._config.get('VAULT_MOUNT_PATH_KV'),
            'VAULT_MOUNT_PATH_APPROLE': self._config.get('VAULT_MOUNT_PATH_APPROLE'),
            'services': {},
            'DEBUG': settings.DEBUG,
            'VAULT_SSL_VERIFY': False,
        }

        context[deploy_module.upper()+'_VAULT_ROLE_ID'] = credentials.get('role_id')
        context[deploy_module.upper()+'_VAULT_SECRET_ID'] = credentials.get('secret_id')

        remove_modules = ['api', 'lapi', 'beat', 'worker-all', 'worker-enrolment', 'worker-enrolment-storage',
                          'worker-enrolment-validation', 'worker-verification', 'worker-alerts', 'worker-reporting',
                          'worker']

        deploy_module_lower = deploy_module.lower()
        remove_modules.remove(deploy_module_lower)

        modules = get_modules()
        for rm_module in remove_modules:
            del modules[rm_module]

        context['services'] = [modules[module] for module in modules]

        return self._create_swarm_service(deploy_module_lower, 'core/module/swarm/core.yaml', context)

    def _remove_core_module(self, deploy_module) -> dict:
        """
           Deploy API
        """
        context = {
            'DEPLOYMENT_SECRETS_PATH': self._config.get('DEPLOYMENT_SECRETS_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'DEPLOYMENT_IMAGE': self._config.get('DEPLOYMENT_IMAGE'),
            'DEPLOYMENT_VERSION': self._config.get('DEPLOYMENT_VERSION'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB'),
            'VAULT_URL': self._config.get('VAULT_URL'),
            'VAULT_MOUNT_PATH_KV': self._config.get('VAULT_MOUNT_PATH_KV'),
            'VAULT_MOUNT_PATH_APPROLE': self._config.get('VAULT_MOUNT_PATH_APPROLE'),
            'services': {},
            'DEBUG': settings.DEBUG,
            'VAULT_SSL_VERIFY': False,
        }

        context[deploy_module.upper()+'_VAULT_ROLE_ID'] = ''
        context[deploy_module.upper()+'_VAULT_SECRET_ID'] = ''

        remove_modules = ['api', 'lapi', 'beat', 'worker-all', 'worker-enrolment', 'worker-enrolment-storage',
                          'worker-enrolment-validation', 'worker-verification', 'worker-alerts', 'worker-reporting']

        deploy_module_lower = deploy_module.lower()
        remove_modules.remove(deploy_module_lower)

        modules = get_modules()
        for rm_module in remove_modules:
            del modules[rm_module]

        context['services'] = [modules[module] for module in modules]

        return self._remove_swarm_service(deploy_module_lower, 'core/module/swarm/core.yaml', context)

    def _get_core_module_status(self, module) -> ServiceDeploymentInformation:
        """
            Get the deployment information for TeSLA CE Moodle
        """
        return self._create_status_obj(module.lower())

    def _get_core_module_script(self, credentials, script_module):
        """
           Deploy API
        """
        context = {
            'DEPLOYMENT_SECRETS_PATH': self._config.get('DEPLOYMENT_SECRETS_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'DEPLOYMENT_IMAGE': self._config.get('DEPLOYMENT_IMAGE'),
            'DEPLOYMENT_VERSION': self._config.get('DEPLOYMENT_VERSION'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB'),
            'VAULT_URL': self._config.get('VAULT_URL'),
            'VAULT_MOUNT_PATH_KV': self._config.get('VAULT_MOUNT_PATH_KV'),
            'VAULT_MOUNT_PATH_APPROLE': self._config.get('VAULT_MOUNT_PATH_APPROLE'),
            'services': {},
            'DEBUG': settings.DEBUG,
            'VAULT_SSL_VERIFY': False,
        }

        context[script_module.upper()+'_VAULT_ROLE_ID'] = credentials.get('role_id')
        context[script_module.upper()+'_VAULT_SECRET_ID'] = credentials.get('secret_id')

        remove_modules = ['api', 'lapi', 'beat', 'worker-all', 'worker-enrolment', 'worker-enrolment-storage',
                          'worker-enrolment-validation', 'worker-verification', 'worker-alerts', 'worker-reporting',
                          'worker']

        deploy_module_lower = script_module.lower()
        remove_modules.remove(deploy_module_lower)

        modules = get_modules()
        for rm_module in remove_modules:
            del modules[rm_module]

        context['services'] = [modules[module] for module in modules]

        task_def = self._remove_empty_lines(render_to_string('core/module/swarm/core.yaml', context))

        script = SetupOptions()
        script.add_command(
            command='docker stack -t tesla_{}.yaml tesla'.format(script_module.lower()),
            description='Create new service for {}'.format(script_module.lower())
        )

        script.add_file(
            filename='tesla_{}.yaml'.format(script_module.lower()),
            description='Stack description for {}'.format(script_module.lower()),
            content=task_def,
            mimetype='application/yaml'
        )

        script.add_file(
            filename='secrets/{}_VAULT_ROLE_ID'.format(script_module.upper()),
            description='Secret {}_VAULT_ROLE_ID'.format(script_module.upper()),
            content=credentials.get('role_id'),
            mimetype='text/plain'
        )

        script.add_file(
            filename='secrets/{}_VAULT_SECRET_ID'.format(script_module.upper()),
            description='Secret {}_VAULT_SECRET_ID'.format(script_module.upper()),
            content=credentials.get('secret_id'),
            mimetype='text/plain'
        )

        return script

    def _deploy_instrument_provider(self, credentials, provider) -> dict:
        """
           Deploy API
        """
        context = {
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'provider': provider,
            'DEBUG': settings.DEBUG,
            'SSL_VERIFY': False
        }
        context["{}_ROLE_ID".format(provider.get('acronym').upper())] = credentials.get('role_id')
        context["{}_SECRET_ID".format(provider.get('acronym').upper())] = credentials.get('secret_id')

        provider_name = "{}_provider".format(provider.get('acronym').lower())

        return self._create_swarm_service(provider_name, 'provider/swarm/provider.yaml', context)

    def _remove_instrument_provider(self, provider) -> dict:
        """
           Deploy API
        """
        context = {
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'provider': provider,
            'DEBUG': settings.DEBUG,
            'SSL_VERIFY': False
        }
        context["{}_ROLE_ID".format(provider.get('acronym').upper())] = ''
        context["{}_SECRET_ID".format(provider.get('acronym').upper())] = ''

        provider_name = "{}_provider".format(provider.get('acronym').lower())

        return self._remove_swarm_service(provider_name, 'provider/swarm/provider.yaml', context)

    def _get_instrument_provider_status(self, module):
        return self._create_status_obj("{}_provider".format(module.lower()))

    def _get_instrument_provider_script(self, module, credentials, provider):
        """
            Get the script to deploy Instrument provider
        """
        context = {
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'provider': provider,
            'DEBUG': settings.DEBUG,
            'SSL_VERIFY': False
        }
        context["{}_ROLE_ID".format(provider.get('acronym').upper())] = credentials.get('role_id')
        context["{}_SECRET_ID".format(provider.get('acronym').upper())] = credentials.get('secret_id')

        task_def = self._remove_empty_lines(render_to_string('provider/swarm/provider.yaml', context))

        script = SetupOptions()
        script.add_command(
            command='docker stack -t tesla_{}_provider.yaml tesla'.format(provider.get('acronym')),
            description='Create new service for {}'.format(provider.get('acronym'))
        )

        script.add_file(
            filename='tesla_{}_provider.yaml'.format(provider.get('acronym')),
            description='Stack description for {} provider'.format(provider.get('acronym')),
            content=task_def,
            mimetype='application/yaml'
        )

        script.add_file(
            filename='secrets/{}_ROLE_ID'.format(provider.get('acronym').upper()),
            description='Secret {}_ROLE_ID'.format(provider.get('acronym').upper()),
            content=credentials.get('role_id'),
            mimetype='text/plain'
        )

        script.add_file(
            filename='secrets/{}_SECRET_ID'.format(provider.get('acronym').upper()),
            description='Secret {}_SECRET_ID'.format(provider.get('acronym').upper()),
            content=credentials.get('secret_id'),
            mimetype='text/plain'
        )

        return script

    def _get_moodle_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for TeSLA CE LAPI
        """
        return self._create_status_obj('moodle')

    def _deploy_moodle(self, credentials) -> dict:
        """
           Deploy API
        """

        context = {
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB'),
            'MOODLE_ROLE_ID': credentials.get('role_id'),
            'MOODLE_SECRET_ID': credentials.get('secret_id'),
            'MOODLE_DB_HOST': self._config.get('MOODLE_DB_HOST'),
            'MOODLE_DB_USER': self._config.get('MOODLE_DB_USER'),
            'MOODLE_DB_NAME': self._config.get('MOODLE_DB_NAME'),
            'MOODLE_DB_PORT': self._config.get('MOODLE_DB_PORT'),
            'MOODLE_DB_PASSWORD': self._config.get('MOODLE_DB_PASSWORD'),
            'MOODLE_DB_PREFIX': self._config.get('MOODLE_DB_PREFIX'),
            'MOODLE_CRON_INTERVAL': self._config.get('MOODLE_CRON_INTERVAL'),
            'MOODLE_FULL_NAME': self._config.get('MOODLE_FULL_NAME'),
            'MOODLE_SHORT_NAME': self._config.get('MOODLE_SHORT_NAME'),
            'MOODLE_SUMMARY': self._config.get('MOODLE_SUMMARY'),
            'MOODLE_ADMIN_USER': self._config.get('MOODLE_ADMIN_USER'),
            'MOODLE_ADMIN_EMAIL': self._config.get('MOODLE_ADMIN_EMAIL'),
            'MOODLE_ADMIN_PASSWORD': self._config.get('MOODLE_ADMIN_PASSWORD'),
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH')
        }

        return self._create_swarm_service('moodle', 'moodle/swarm/moodle.yaml', context)

    def _remove_moodle(self) -> dict:
        """
           Deploy API
        """
        context = {
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB'),
            'MOODLE_ROLE_ID': '',
            'MOODLE_SECRET_ID': '',
            'MOODLE_DB_HOST': self._config.get('MOODLE_DB_HOST'),
            'MOODLE_DB_USER': self._config.get('MOODLE_DB_USER'),
            'MOODLE_DB_NAME': self._config.get('MOODLE_DB_NAME'),
            'MOODLE_DB_PORT': self._config.get('MOODLE_DB_PORT'),
            'MOODLE_DB_PASSWORD': self._config.get('MOODLE_DB_PASSWORD'),
            'MOODLE_DB_PREFIX': self._config.get('MOODLE_DB_PREFIX'),
            'MOODLE_CRON_INTERVAL': self._config.get('MOODLE_CRON_INTERVAL'),
            'MOODLE_FULL_NAME': self._config.get('MOODLE_FULL_NAME'),
            'MOODLE_SHORT_NAME': self._config.get('MOODLE_SHORT_NAME'),
            'MOODLE_SUMMARY': self._config.get('MOODLE_SUMMARY'),
            'MOODLE_ADMIN_USER': self._config.get('MOODLE_ADMIN_USER'),
            'MOODLE_ADMIN_EMAIL': self._config.get('MOODLE_ADMIN_EMAIL'),
            'MOODLE_ADMIN_PASSWORD': self._config.get('MOODLE_ADMIN_PASSWORD'),
        }
        return self._remove_swarm_service('moodle', 'moodle/swarm/moodle.yaml', context)

    def _get_moodle_script(self, credentials):
        """
            Get the script to deploy Instrument provider
        """
        context = {
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'DEPLOYMENT_LB': self._config.get('DEPLOYMENT_LB'),
            'MOODLE_ROLE_ID': '',
            'MOODLE_SECRET_ID': '',
            'MOODLE_DB_HOST': self._config.get('MOODLE_DB_HOST'),
            'MOODLE_DB_USER': self._config.get('MOODLE_DB_USER'),
            'MOODLE_DB_NAME': self._config.get('MOODLE_DB_NAME'),
            'MOODLE_DB_PORT': self._config.get('MOODLE_DB_PORT'),
            'MOODLE_DB_PASSWORD': self._config.get('MOODLE_DB_PASSWORD'),
            'MOODLE_DB_PREFIX': self._config.get('MOODLE_DB_PREFIX'),
            'MOODLE_CRON_INTERVAL': self._config.get('MOODLE_CRON_INTERVAL'),
            'MOODLE_FULL_NAME': self._config.get('MOODLE_FULL_NAME'),
            'MOODLE_SHORT_NAME': self._config.get('MOODLE_SHORT_NAME'),
            'MOODLE_SUMMARY': self._config.get('MOODLE_SUMMARY'),
            'MOODLE_ADMIN_USER': self._config.get('MOODLE_ADMIN_USER'),
            'MOODLE_ADMIN_EMAIL': self._config.get('MOODLE_ADMIN_EMAIL'),
            'MOODLE_ADMIN_PASSWORD': self._config.get('MOODLE_ADMIN_PASSWORD'),
        }

        task_def = self._remove_empty_lines(render_to_string('moodle/swarm/moodle.yaml', context))

        script = SetupOptions()
        script.add_command(
            command='docker stack -t tesla_moodle.yaml tesla',
            description='Create new service for moodle'
        )

        script.add_file(
            filename='tesla_moodle.yaml',
            description='Stack description for moodle',
            content=task_def,
            mimetype='application/yaml'
        )

        script.add_file(
            filename='secrets/MOODLE_ROLE_ID',
            description='Secret MOODLE_ROLE_ID',
            content=credentials.get('role_id'),
            mimetype='text/plain'
        )

        script.add_file(
            filename='secrets/MOODLE_SECRET_ID',
            description='Secret MOODLE_SECRET_ID',
            content=credentials.get('secret_id'),
            mimetype='text/plain'
        )

        script.add_file(
            filename='secrets/MOODLE_DB_PASSWORD',
            description='Secret MOODLE_DB_PASSWORD',
            content=self._config.get('MOODLE_DB_PASSWORD'),
            mimetype='text/plain'
        )

        script.add_file(
            filename='secrets/MOODLE_ADMIN_PASSWORD',
            description='Secret MOODLE_ADMIN_PASSWORD',
            content=self._config.get('MOODLE_ADMIN_PASSWORD'),
            mimetype='text/plain'
        )

        return script

    def reboot_module(self, module: str, wait_ready: bool = True):
        """
            Reboot module
        """

        service_id = '{}_{}'.format(self.config.get('SWARM_SERVICE_PREFIX'), module)
        try:
            # Check if service exist
            service = self.client.services.get(service_id)

            service.force_update()

        except docker.errors.NotFound:
            return False

        return True