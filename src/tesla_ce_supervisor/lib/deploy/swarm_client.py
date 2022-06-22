import docker
from docker.types.healthcheck import Healthcheck
from docker.types.services import EndpointSpec, SecretReference
import os
import typing
import yaml

from django.template.loader import render_to_string
from yaml.loader import SafeLoader


from .base import BaseDeploy
from ..models.check import ServiceDeploymentInformation, ConnectionStatus
from ..setup_options import SetupOptions
from ..tesla.conf import Config


class SwarmConfig:
    """
        Swarm configuration
    """
    # Base url address
    swarm_base_url: str = 'unix:///var/run/docker.sock'

    # Client key file path
    client_key_file_path: int = 4646
    client_key_file: str = ''

    # Client certificate file path
    client_cert_file_path: int = 4646
    client_cert_file: str = ''

    # Specific CA certificate path
    specific_ca_cert_path: int = 4646
    specific_ca_cert: str = ''

    def __init__(self, config,
                 swarm_service_prefix: typing.Optional[str] = None,
                 swarm_base_url: typing.Optional[str] = None,
                 client_key_file_path: typing.Optional[int] = None,
                 client_key_file: typing.Optional[str] = None,
                 client_cert_file_path: typing.Optional[typing.Optional[int]] = None,
                 client_cert_file: typing.Optional[typing.Optional[str]] = None,
                 specific_ca_cert_path: typing.Optional[typing.Optional[int]] = None,
                 specific_ca_cert: typing.Optional[typing.Optional[str]] = None
                 ) -> None:

        # Swarm configuration
        self.swarm_service_prefix = self._set_value(config, swarm_service_prefix, 'SWARM_SERVICE_PREFIX', 'SWARM_SERVICE_PREFIX')
        self.swarm_base_url = self._set_value(config, swarm_base_url, 'SWARM_BASE_URL', 'SWARM_BASE_URL')
        self.client_key_path = self._set_value(config, client_key_file_path, 'SWARM_CLIENT_KEY_PATH', 'SWARM_CLIENT_KEY_PATH')
        self.client_cert_path = self._set_value(config, client_cert_file_path, 'SWARM_CLIENT_CERT_PATH', 'SWARM_CLIENT_CERT_PATH')
        self.specific_ca_cert_path = self._set_value(config, specific_ca_cert_path, 'SWARM_SPECIFIC_CA_CERT_PATH', 'SWARM_SPECIFIC_CA_CERT_PATH')
        self.client_key = self._set_value(config, client_key_file, 'SWARM_CLIENT_KEY', 'SWARM_CLIENT_KEY')
        self.client_cert = self._set_value(config, client_cert_file, 'SWARM_CLIENT_CERT', 'SWARM_CLIENT_CERT')
        self.specific_ca_cert = self._set_value(config, specific_ca_cert, 'SWARM_SPECIFIC_CA_CERT', 'SWARM_SPECIFIC_CA_CERT')

    @staticmethod
    def _set_value(config, parameter, env_key=None, conf_key=None, default=None):
        if parameter is not None:
            return parameter
        default_value = None
        if conf_key is not None:
            default_value = config.get(conf_key)
        if env_key is not None:
            ret_val = os.getenv(env_key, default_value)
        else:
            ret_val = default_value
        if ret_val is None:
            ret_val = default
        return ret_val

class SwarmDeploy(BaseDeploy):
    # Swarm configuration
    # swarm_conf: typing.Optional[SwarmConfig] = None

    def __init__(self, config: typing.Optional[Config] = None, swarm_conf: typing.Optional[SwarmConfig] = None) -> None:
        super().__init__(config)
        self.swarm_conf = swarm_conf
        if self.swarm_conf is None:
            self.swarm_conf = SwarmConfig(config)

        self._client = docker.DockerClient(base_url=self.swarm_conf.swarm_base_url)

        assert self._client is not None


    def _create_status_obj(self, name: str) -> ServiceDeploymentInformation:
        # Check if job exists
        '''
        job_info = None
        if len(self._client.jobs.get_jobs(name)) == 1:
            job_info = self._client.job.get_deployment(name)
        '''
        service_id = '{}_{}'.format(self.swarm_conf.swarm_service_prefix, name)
        status = ServiceDeploymentInformation(service_id, 'swarm', {})

        try:
            service = self._client.services.get(service_id)
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

    def _remove_swarm_service(self, name: str) -> dict:
        service_id = '{}_{}'.format(self.swarm_conf.swarm_service_prefix, name)
        try:
            service = self._client.services.get(service_id)
            service.remove()
        except docker.errors.DockerException:
            pass

        return {}

    def _create_swarm_service(self, name: str, template: str, context: dict) -> dict:

        task_def = self._remove_empty_lines(render_to_string(template, context))

        task_def_dict = yaml.load(task_def, Loader=SafeLoader)
        service_def_dict = task_def_dict['services'][name]
        service_def_dict['name'] = '{}_{}'.format(self.swarm_conf.swarm_service_prefix, name)

        image = service_def_dict['image']
        del service_def_dict['image']

        command = None
        if 'command' in service_def_dict:
            command = service_def_dict['command']
            del service_def_dict['command']
            service_def_dict['args'] = command

            if type(service_def_dict['args']) == str:
                service_def_dict['args'] = [service_def_dict['args']]

        if 'entrypoint' in service_def_dict:
            command = service_def_dict['entrypoint']
            del service_def_dict['entrypoint']

        # contraints, rrestart policy, etc...
        for key in service_def_dict['deploy'].keys():
            if key == 'placement':
                for subkey in service_def_dict['deploy'][key].keys():
                    service_def_dict[subkey] = service_def_dict['deploy'][key][subkey]
            elif key != 'replicas':
                service_def_dict[key] = service_def_dict['deploy'][key]

        del service_def_dict['deploy']

        # ports
        endpoint_spec = None
        if 'ports' in service_def_dict:
            res_ports = []
            for port in service_def_dict['ports']:
                aux = {
                    'TargetPort': int(port.split(':')[0]),
                    'PublishedPort': int(port.split(':')[1])
                }
                res_ports.append(aux)

            service_def_dict['endpoint_spec'] = EndpointSpec(ports=res_ports)

            del service_def_dict['ports']


        # check if all networks are created:
        networks_rename = []
        for net in service_def_dict['networks']:
            try:
                network_id = '{}_{}'.format(self.swarm_conf.swarm_service_prefix, net)
                network = self._client.networks.get(network_id)
                # in this case netowrk exists
                networks_rename.append(network_id)
            except docker.errors.NotFound:
                self._client.networks.create(name=network_id, driver='overlay')
                networks_rename.append(network_id)
            except docker.errors.DockerException:
                pass

        service_def_dict['networks'] = networks_rename

        # check volumes
        if 'volumes' in task_def_dict and task_def_dict['volumes'] is not None:
            for vol in task_def_dict['volumes']:
                try:
                    volume_id = vol
                    volume = self._client.volumes.get(volume_id)
                except docker.errors.NotFound:
                    driver_opts = task_def_dict['volumes'][vol]['driver_opts']
                    self._client.volumes.create(name=volume_id, driver='local', driver_opts=driver_opts)
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
                try:
                    secret_id = sec.upper()
                    secret = self._client.secrets.get(secret_id)
                    secrets_rename.append(SecretReference(secret_id=secret.attrs['ID'],
                                                          secret_name=secret.name))
                except docker.errors.NotFound:
                    secret_data = context[sec]
                    secret = self._client.secrets.create(name=secret_id, data=secret_data)
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
        if 'configs' in service_def_dict:
            del service_def_dict['configs']

        try:
            self._client.services.create(image=image, command=None, **service_def_dict)
        except docker.errors.DockerException as err:
            print(err)
            pass
        return {}

    def write_scripts(self) -> None:
        """
            Write deployment scripts
        """
        pass

    def deploy_lb(self) -> dict:
        """
            Deploy Load Balancer
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_ADMIN_MAIL': self._config.get('TESLA_ADMIN_MAIL')
        }

        return self._create_swarm_service('traefik', 'lb/traefik/swarm/traefik.yaml', context)

    def get_lb_script(self) -> SetupOptions:
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

    def get_lb_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for Load Balancer
        """
        return self._create_status_obj('traefik')

    def deploy_vault(self) -> dict:
        """
            Deploy Hashicorp Vault
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN')
        }

        return self._create_swarm_service('vault', 'services/vault/swarm/vault.yaml', context)

    def get_vault_script(self) -> SetupOptions:
        """
            Get the script to deploy Hashicorp Vault
        """
        script = SetupOptions()
        return script

    def deploy_minio(self) -> dict:
        """
            Deploy MinIO
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'STORAGE_REGION': self._config.get('STORAGE_REGION'),
            'STORAGE_ACCESS_KEY': self._config.get('STORAGE_ACCESS_KEY'),
            'STORAGE_SECRET_KEY': self._config.get('STORAGE_SECRET_KEY'),
        }

        return self._create_swarm_service('minio', 'services/minio/swarm/minio.yaml', context)

    def get_minio_script(self) -> SetupOptions:
        """
            Get the script to deploy MinIO
        """
        script = SetupOptions()
        return script

    def deploy_redis(self) -> dict:
        """
            Deploy Redis
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'REDIS_PASSWORD': self._config.get('REDIS_PASSWORD'),
        }

        return self._create_swarm_service('redis', 'services/redis/swarm/redis.yaml', context)

    def get_redis_script(self) -> SetupOptions:
        """
            Get the script to deploy Redis
        """
        script = SetupOptions()
        return script

    def deploy_database(self) -> dict:
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
            raise TeslaDeployNomadException('Invalid database engine')

        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'DB_ROOT_PASSWORD': self._config.get('DB_ROOT_PASSWORD'),
            'DB_PASSWORD': self._config.get('DB_PASSWORD'),
            'DB_USER': self._config.get('DB_USER'),
            'DB_NAME': self._config.get('DB_NAME'),
        }

        return self._create_swarm_service('database', template, context)

    def get_database_script(self) -> SetupOptions:
        """
            Get the script to deploy Database
        """
        script = SetupOptions()
        return script

    def deploy_rabbitmq(self) -> dict:
        """
           Deploy RabbitMQ
        """
        context = {
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'RABBITMQ_ADMIN_USER': self._config.get('RABBITMQ_ADMIN_USER'),
            'RABBITMQ_ADMIN_PASSWORD': self._config.get('RABBITMQ_ADMIN_PASSWORD'),
            'RABBITMQ_ERLANG_COOKIE': self._config.get('RABBITMQ_ERLANG_COOKIE'),
        }

        return self._create_swarm_service('rabbitmq', 'services/rabbitmq/swarm/rabbitmq.yaml', context)

    def get_rabbit_script(self) -> SetupOptions:
        """
            Get the script to deploy RabbitMQ
        """
        script = SetupOptions()
        return script

    def remove_lb(self) -> dict:
        return self._remove_swarm_service('traefik')

    def remove_vault(self) -> dict:
        return self._remove_swarm_service('vault')

    def get_vault_status(self) -> ServiceDeploymentInformation:
        return self._create_status_obj('vault')

    def remove_minio(self) -> dict:
        return self._remove_swarm_service('minio')

    def get_minio_status(self) -> ServiceDeploymentInformation:
        return self._create_status_obj('minio')

    def remove_redis(self) -> dict:
        return self._remove_swarm_service('redis')

    def get_redis_status(self) -> ServiceDeploymentInformation:
        return self._create_status_obj('redis')

    def remove_database(self) -> dict:
        return self._remove_swarm_service('database')

    def get_database_status(self) -> ServiceDeploymentInformation:
        return self._create_status_obj('database')

    def remove_rabbitmq(self) -> dict:
        return self._remove_swarm_service('rabbitmq')

    def get_rabbitmq_script(self) -> SetupOptions:
        pass

    def get_rabbitmq_status(self) -> ServiceDeploymentInformation:
        return self._create_status_obj('rabbitmq')

    def test_connection(self) -> ConnectionStatus:
        pass

