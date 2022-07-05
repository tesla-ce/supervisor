import os
import typing
import nomad
from django.template.loader import render_to_string
from .base import BaseDeploy, ServiceDeploymentInformation
from .exceptions import TeslaDeployNomadTemplateException, TeslaDeployNomadException
from ..models.check import ConnectionStatus
from ..tesla.conf import Config
from ..setup_options import SetupOptions


class NomadConfig:
    """
        Nomad configuration
    """
    # Nomad server URL
    nomad_addr: str = 'http://127.0.0.1'

    # Nomad server port
    nomad_port: int = 4646

    # Nomad region
    nomad_region: str = 'global'

    # Nomad datacenters
    nomad_datacenters: typing.List[str] = []

    # Authentication
    nomad_auth: typing.Optional[typing.Union[typing.Literal["ACL"], typing.Literal["CERT"]]] = None

    # Nomad SecretID of an ACL token for authentication
    nomad_token: typing.Optional[str] = None

    # Path to a PEM encoded client certificate for TLS authentication
    nomad_client_cert: typing.Optional[str] = None

    # Path to an unencrypted PEM encoded private key matching the client certificate for TLS authentication
    nomad_client_key: typing.Optional[str] = None

    # Path to a PEM encoded CA cert file to use to verify the Nomad server SSL certificate.
    nomad_cacert: typing.Optional[str] = None

    # Path to a directory of PEM encoded CA cert files to verify the Nomad server SSL certificate.
    nomad_capath: typing.Optional[str] = None

    # Do not verify TLS certificate. This is highly not recommended.
    nomad_skip_verify: typing.Optional[bool] = False

    # The server name to use as the SNI host when connecting via TLS.
    nomad_tls_server_name: typing.Optional[str] = None

    def __init__(self, config, nomad_addr: typing.Optional[str] = None,
                 nomad_region: typing.Optional[str] = None,
                 nomad_datacenters: typing.Optional[typing.List[str]] = None,
                 nomad_auth: typing.Optional[typing.Union[typing.Literal["ACL"], typing.Literal["CERT"]]] = None,
                 nomad_token: typing.Optional[str] = None,
                 nomad_client_cert: typing.Optional[str] = None,
                 nomad_client_key: typing.Optional[str] = None,
                 nomad_cacert: typing.Optional[str] = None,
                 nomad_capath: typing.Optional[str] = None,
                 nomad_skip_verify: typing.Optional[bool] = False,
                 nomad_tls_server_name: typing.Optional[str] = None,
                 ) -> None:

        # Nomad configuration
        self.nomad_datacenters = self._set_value(
            config, nomad_datacenters, 'NOMAD_DATACENTERS', 'NOMAD_DATACENTERS', []
        )
        self.nomad_auth = self._set_value(
            config, nomad_auth
        )
        self.nomad_addr = self._set_value(config, nomad_addr, 'NOMAD_ADDR', 'NOMAD_ADDR')
        self.nomad_region = self._set_value(config, nomad_region, 'NOMAD_REGION', 'NOMAD_REGION')

        # Verification
        self.nomad_skip_verify = self._set_value(
            config, nomad_skip_verify, 'NOMAD_SKIP_VERIFY', 'NOMAD_SKIP_VERIFY'
        )
        self.nomad_tls_server_name = self._set_value(
            config, nomad_tls_server_name, 'NOMAD_TLS_SERVER_NAME', 'NOMAD_TLS_SERVER_NAME'
        )
        self.nomad_cacert = os.getenv('NOMAD_CACERT', nomad_cacert)
        self.nomad_capath = os.getenv('NOMAD_CAPATH', nomad_capath)

        # Authentication configuration
        if self.nomad_auth == "ACL":
            self.nomad_token = self._set_value(nomad_token, 'NOMAD_TOKEN', 'NOMAD_ACL_TOKEN')
        elif self.nomad_auth == "CERT":
            self.nomad_token = self._set_value(nomad_client_cert, 'NOMAD_CLIENT_CERT', 'NOMAD_CLIENT_CERT')
            self.nomad_token = self._set_value(nomad_client_key, 'NOMAD_CLIENT_KEY', 'NOMAD_CLIENT_KEY')

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


class NomadDeploy(BaseDeploy):
    """
        Utility class for Nomad deployment
    """
    # Nomad configuration
    nomad_conf: typing.Optional[NomadConfig] = None

    def __init__(self, config: typing.Optional[Config] = None, nomad_conf: typing.Optional[NomadConfig] = None) -> None:
        super().__init__(config)
        self.nomad_conf = nomad_conf
        if self.nomad_conf is None:
            self.nomad_conf = NomadConfig(config)
        if self.nomad_conf.nomad_auth is None:
            self._client = nomad.Nomad(
                address=self.nomad_conf.nomad_addr,
                verify=self.nomad_conf.nomad_skip_verify
            )
        elif self.nomad_conf.nomad_auth == "ACL":
            self._client = nomad.Nomad(
                address=self.nomad_conf.nomad_addr,
                token=self.nomad_conf.nomad_token,
                verify=self.nomad_conf.nomad_skip_verify
            )
        elif self.nomad_conf.nomad_auth == "CERT":
            self._client = nomad.Nomad(
                address=self.nomad_conf.nomad_addr,
                cert=(self.nomad_conf.nomad_client_cert,self.nomad_conf.nomad_client_key),
                verify=self.nomad_conf.nomad_skip_verify
            )

    def _create_status_obj(self, name: str) -> ServiceDeploymentInformation:
        # Check if job exists
        job_info = None
        if len(self._client.jobs.get_jobs(name)) == 1:
            job_info = self._client.job.get_deployment(name)
        status = ServiceDeploymentInformation(name, 'nomad', job_info)
        if job_info is not None:
            status.jobs_running = job_info['TaskGroups'][name]['PlacedAllocs']
            status.jobs_expected = job_info['TaskGroups'][name]['DesiredTotal']
            status.jobs_healthy = job_info['TaskGroups'][name]['HealthyAllocs']
            if job_info['Status'] == 'running':
                status.status = 'waiting'
            elif job_info['Status'] == 'successful':
                status.status = 'success'
            else:
                status.status = 'error'
        return status

    def _crete_nomad_job(self, name: str, template: str, context: dict) -> dict:
        task_def = self._remove_empty_lines(render_to_string(template, context))

        try:
            job_def = self._client.jobs.parse(task_def)
        except nomad.api.exceptions.BadRequestNomadException as err:
            raise TeslaDeployNomadTemplateException(err.nomad_resp.text) from err

        try:
            response = self._client.job.register_job(name, {'Job': job_def})
        except nomad.api.exceptions.BadRequestNomadException as err:
            raise TeslaDeployNomadException(err.nomad_resp.text) from err
        except nomad.api.exceptions.BaseNomadException as err:
            raise TeslaDeployNomadException(err.nomad_resp.text) from err

        return response

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
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'traefik_image': 'traefik:v2.5',
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_ADMIN_MAIL': self._config.get('TESLA_ADMIN_MAIL')
        }

        return self._crete_nomad_job('traefik', 'lb/traefik/nomad/traefik.nomad', context)

    def remove_lb(self) -> dict:
        """
            Remove deployed Load Balancer
        """
        return self._client.job.deregister_job('traefik', True)

    def get_lb_script(self) -> SetupOptions:
        """
            Get the script to deploy Load Balancer
        """
        context = {
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'traefik_image': 'traefik:v2.5',
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_ADMIN_MAIL': self._config.get('TESLA_ADMIN_MAIL')
        }

        task_def = self._remove_empty_lines(render_to_string('lb/traefik/nomad/traefik.nomad', context))

        script = SetupOptions()
        script.add_command(
            command='nomad job run tesla-ce-lb-traefik.nomad',
            description='Create new Nomad job for Traefik Load Balancer'
        )
        script.add_file(
            filename='tesla-ce-lb-traefik.nomad',
            description='Job description for Traefik Load Balancer',
            content=task_def,
            mimetype='application/hcl'
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
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'vault_image': 'vault',
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN')
        }

        return self._crete_nomad_job('vault', 'services/vault/nomad/vault.nomad', context)

    def remove_vault(self) -> dict:
        """
            Remove deployed Vault
        """
        return self._client.job.deregister_job('vault', True)

    def get_vault_script(self) -> SetupOptions:
        """
            Get the script to deploy Hashicorp Vault
        """
        context = {
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'vault_image': 'vault',
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN')
        }

        task_def = self._remove_empty_lines(render_to_string('services/vault/nomad/vault.nomad', context))

        script = SetupOptions()
        script.add_command(
            command='nomad job run tesla-ce-vault.nomad',
            description='Create new Nomad job for Vault'
        )
        script.add_file(
            filename='tesla-ce-vault.nomad',
            description='Job description for Vault',
            content=task_def,
            mimetype='application/hcl'
        )

        return script

    def get_vault_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for Vault
        """
        return self._create_status_obj('vault')

    def deploy_minio(self) -> dict:
        """
            Deploy MinIO
        """
        context = {
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'minio_image': 'minio/minio',
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'STORAGE_REGION': self._config.get('STORAGE_REGION'),
            'STORAGE_ACCESS_KEY': self._config.get('STORAGE_ACCESS_KEY'),
            'STORAGE_SECRET_KEY': self._config.get('STORAGE_SECRET_KEY'),
        }

        return self._crete_nomad_job('minio', 'services/minio/nomad/minio.nomad', context)

    def remove_minio(self) -> dict:
        """
            Remove deployed MinIO
        """
        return self._client.job.deregister_job('minio', True)

    def get_minio_script(self) -> SetupOptions:
        """
            Get the script to deploy MinIO
        """
        context = {
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'minio_image': 'minio/minio',
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'STORAGE_REGION': self._config.get('STORAGE_REGION'),
            'STORAGE_ACCESS_KEY': self._config.get('STORAGE_ACCESS_KEY'),
            'STORAGE_SECRET_KEY': self._config.get('STORAGE_SECRET_KEY'),
        }
        task_def = self._remove_empty_lines(render_to_string('services/minio/nomad/minio.nomad', context))

        script = SetupOptions()
        script.add_command(
            command='nomad job run tesla-ce-minio.nomad',
            description='Create new Nomad job for MinIO'
        )
        script.add_file(
            filename='tesla-ce-minio.nomad',
            description='Job description for MinIO',
            content=task_def,
            mimetype='application/hcl'
        )

        return script

    def get_minio_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for MinIO
        """
        return self._create_status_obj('minio')

    def deploy_redis(self) -> dict:
        """
            Deploy Redis
        """
        context = {
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'redis_image': 'redis:alpine',
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'REDIS_PASSWORD': self._config.get('REDIS_PASSWORD'),
        }

        return self._crete_nomad_job('redis', 'services/redis/nomad/redis.nomad', context)

    def remove_redis(self) -> dict:
        """
            Remove deployed Redis
        """
        return self._client.job.deregister_job('redis', True)

    def get_redis_script(self) -> SetupOptions:
        """
            Get the script to deploy Redis
        """
        context = {
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'redis_image': 'redis:alpine',
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'REDIS_PASSWORD': self._config.get('REDIS_PASSWORD'),
        }
        task_def = self._remove_empty_lines(render_to_string('services/redis/nomad/redis.nomad', context))

        script = SetupOptions()
        script.add_command(
            command='nomad job run tesla-ce-redis.nomad',
            description='Create new Nomad job for Redis'
        )
        script.add_file(
            filename='tesla-ce-redis.nomad',
            description='Job description for Redis',
            content=task_def,
            mimetype='application/hcl'
        )

        return script

    def get_redis_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for Redis
        """
        return self._create_status_obj('redis')

    def deploy_database(self) -> dict:
        """
            Deploy Database
        """
        if self._config.get('DB_ENGINE') == 'mysql':
            db_image = 'mariadb'
            name = 'mysql'
            template = 'services/database/mysql/nomad/mysql.nomad'
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
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'db_image': db_image,
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'DB_ROOT_PASSWORD': self._config.get('DB_ROOT_PASSWORD'),
            'DB_PASSWORD': self._config.get('DB_PASSWORD'),
            'DB_USER': self._config.get('DB_USER'),
            'DB_NAME': self._config.get('DB_NAME'),
        }

        return self._crete_nomad_job(name, template, context)

    def remove_database(self) -> dict:
        """
            Remove deployed Database
        """
        if self._config.get('DB_ENGINE') == 'mysql':
            name = 'mysql'
        elif self._config.get('DB_ENGINE') == 'postgresql':
            name = None
        else:
            name = None

        if name is None:
            raise TeslaDeployNomadException('Invalid database engine')
        return self._client.job.deregister_job(name, True)

    def get_database_script(self) -> SetupOptions:
        """
            Get the script to deploy Database
        """
        if self._config.get('DB_ENGINE') == 'mysql':
            db_image = 'mariadb'
            name = 'mysql'
            template = 'services/database/mysql/nomad/mysql.nomad'
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
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'db_image': db_image,
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'DB_ROOT_PASSWORD': self._config.get('DB_ROOT_PASSWORD'),
            'DB_PASSWORD': self._config.get('DB_PASSWORD'),
            'DB_USER': self._config.get('DB_USER'),
            'DB_NAME': self._config.get('DB_NAME'),
        }
        task_def = self._remove_empty_lines(render_to_string(template, context))

        script = SetupOptions()
        script.add_command(
            command='nomad job run tesla-ce-database.nomad',
            description='Create new Nomad job for {} database'.format(name)
        )
        script.add_file(
            filename='tesla-ce-database.nomad',
            description='Job description for {} database'.format(name),
            content=task_def,
            mimetype='application/hcl'
        )

        return script

    def get_database_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for Database
        """
        return self._create_status_obj(self._config.get('DB_ENGINE'))

    def deploy_rabbitmq(self) -> dict:
        """
            Deploy RabbitMQ
        """
        context = {
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'rabbitmq_image': 'rabbitmq:3.8-management-alpine',
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'RABBITMQ_ADMIN_USER': self._config.get('RABBITMQ_ADMIN_USER'),
            'RABBITMQ_ADMIN_PASSWORD': self._config.get('RABBITMQ_ADMIN_PASSWORD'),
            'RABBITMQ_ERLANG_COOKIE': self._config.get('RABBITMQ_ERLANG_COOKIE'),
        }

        return self._crete_nomad_job('rabbitmq', 'services/rabbitmq/nomad/rabbitmq.nomad', context)

    def remove_rabbitmq(self) -> dict:
        """
            Remove deployed RabbitMQ
        """
        return self._client.job.deregister_job('rabbitmq', True)

    def get_rabbitmq_script(self) -> SetupOptions:
        """
            Get the script to deploy RabbitMQ
        """
        context = {
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'rabbitmq_image': 'rabbitmq:3.8-management-alpine',
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'RABBITMQ_ADMIN_USER': self._config.get('RABBITMQ_ADMIN_USER'),
            'RABBITMQ_ADMIN_PASSWORD': self._config.get('RABBITMQ_ADMIN_PASSWORD'),
            'RABBITMQ_ERLANG_COOKIE': self._config.get('RABBITMQ_ERLANG_COOKIE'),
        }
        task_def = self._remove_empty_lines(render_to_string('services/rabbitmq/nomad/rabbitmq.nomad', context))

        script = SetupOptions()
        script.add_command(
            command='nomad job run tesla-ce-rabbitmq.nomad',
            description='Create new Nomad job for RabbitMQ'
        )
        script.add_file(
            filename='tesla-ce-rabbitmq.nomad',
            description='Job description for RabbitMQ',
            content=task_def,
            mimetype='application/hcl'
        )

        return script

    def get_rabbitmq_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for RabbitMQ
        """
        return self._create_status_obj('rabbitmq')

    def deploy_supervisor(self) -> dict:
        """
            Deploy TeSLA CE Supervisor
        """
        context = {
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'supervisor_image': 'teslace/supervisor:latest',
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'SUPERVISOR_SECRET': self._config.get('SUPERVISOR_SECRET'),
            'SUPERVISOR_ADMIN_USER': self._config.get('SUPERVISOR_ADMIN_USER'),
            'SUPERVISOR_ADMIN_PASSWORD': self._config.get('SUPERVISOR_ADMIN_PASSWORD'),
            'SUPERVISOR_ADMIN_EMAIL': self._config.get('TESLA_ADMIN_MAIL'),
        }
        return self._crete_nomad_job('tesla_ce_supervisor', 'supervisor/nomad/supervisor.nomad', context)

    def remove_supervisor(self) -> dict:
        """
            Remove deployed TeSLA CE Supervisor
        """
        return self._client.job.deregister_job('tesla_ce_supervisor', True)

    def get_supervisor_script(self) -> SetupOptions:
        """
            Get the script to deploy TeSLA CE Supervisor
        """
        context = {
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'supervisor_image': 'teslace/supervisor:latest',
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            'TESLA_DOMAIN': self._config.get('TESLA_DOMAIN'),
            'SUPERVISOR_SECRET': self._config.get('SUPERVISOR_SECRET'),
            'SUPERVISOR_ADMIN_USER': self._config.get('SUPERVISOR_ADMIN_USER'),
            'SUPERVISOR_ADMIN_PASSWORD': self._config.get('SUPERVISOR_ADMIN_PASSWORD'),
            'SUPERVISOR_ADMIN_EMAIL': self._config.get('TESLA_ADMIN_MAIL'),
        }
        task_def = self._remove_empty_lines(render_to_string('supervisor/nomad/supervisor.nomad', context))

        script = SetupOptions()
        script.add_command(
            command='nomad job run tesla-ce-supervisor.nomad',
            description='Create new Nomad job for TeSLA CE Supervisor'
        )
        script.add_file(
            filename='tesla-ce-supervisor.nomad',
            description='Job description for TeSLA CE Supervisor',
            content=task_def,
            mimetype='application/hcl'
        )

        return script

    def get_supervisor_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for TeSLA CE Supervisor
        """
        return self._create_status_obj('supervisor')

    def test_connection(self) -> ConnectionStatus:
        pass



