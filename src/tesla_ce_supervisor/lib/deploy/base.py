import abc
import typing

from django.contrib.auth.models import User

from .exceptions import TeslaDeployException
from ..setup_options import SetupOptions
from ..tesla.conf import Config
from ..models.check import ServiceDeploymentInformation, ConnectionStatus, CommandStatus

ModuleCode = typing.Union[
    typing.Literal['LB'],
    typing.Literal['DATABASE'],
    typing.Literal['MINIO'],
    typing.Literal['RABBITMQ'],
    typing.Literal['REDIS'],
    typing.Literal['VAULT'],
    typing.Literal['SUPERVISOR'],
]

NOT_IMPLEMENTED_MESSAGE = 'Method not implemented'
INVALID_MODULE_MESSAGE = 'Invalid module name {}. ' \
                         'Valid names are: lb, minio, database, rabbitmq, redis, supervisor, vault.'


class BaseDeploy(abc.ABC):
    """
        Base deployment class. Needs to be extended for each deployment method
    """
    def __init__(self, config: typing.Optional[Config] = None) -> None:
        super().__init__()
        self._config = config

    @abc.abstractmethod
    def test_deployer(self) -> dict:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def test_connection(self) -> ConnectionStatus:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def write_scripts(self) -> None:
        """
            Write deployment scripts
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _deploy_lb(self) -> dict:
        """
            Deploy Load Balancer
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _remove_lb(self) -> dict:
        """
            Remove deployed Load Balancer
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_lb_script(self) -> SetupOptions:
        """
            Get the script to deploy Load Balancer
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_lb_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for Load Balancer
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _deploy_vault(self) -> dict:
        """
            Deploy Hashicorp Vault
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _remove_vault(self) -> dict:
        """
            Remove deployed Vault
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_vault_script(self) -> SetupOptions:
        """
            Get the script to deploy Hashicorp Vault
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_vault_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for Vault
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _deploy_minio(self) -> dict:
        """
            Deploy MinIO
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _remove_minio(self) -> dict:
        """
            Remove deployed MinIO
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_minio_script(self) -> SetupOptions:
        """
            Get the script to deploy MinIO
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_minio_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for MinIO
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _deploy_redis(self) -> dict:
        """
            Deploy Redis
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _remove_redis(self) -> dict:
        """
            Remove deployed Redis
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_redis_script(self) -> SetupOptions:
        """
            Get the script to deploy Redis
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_redis_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for Redis
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _deploy_database(self) -> dict:
        """
            Deploy Database
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _remove_database(self) -> dict:
        """
            Remove deployed Database
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_database_script(self) -> SetupOptions:
        """
            Get the script to deploy Database
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_database_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for Database
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _deploy_rabbitmq(self) -> dict:
        """
            Deploy RabbitMQ
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _remove_rabbitmq(self) -> dict:
        """
            Remove deployed RabbitMQ
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_rabbitmq_script(self) -> SetupOptions:
        """
            Get the script to deploy RabbitMQ
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_rabbitmq_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for RabbitMQ
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @staticmethod
    def _remove_empty_lines(text):
        return '\n'.join([line for line in text.split('\n') if line.strip()])

    @abc.abstractmethod
    def _deploy_supervisor(self) -> dict:
        """
            Deploy TeSLA CE Supervisor
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _remove_supervisor(self) -> dict:
        """
            Remove deployed TeSLA CE Supervisor
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _remove_dashboard(self) -> dict:
        """
            Remove deployed TeSLA CE Dashboard
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    def _remove_moodle(self) -> dict:
        """
            Remove deployed TeSLA CE Moodle
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _remove_core_module(self, module) -> dict:
        """
            Remove deployed TeSLA CE Core module
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _remove_instrument_provider(self, provider) -> dict:
        """
            Remove deployed TeSLA CE Instrument provider module
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_supervisor_script(self) -> SetupOptions:
        """
            Get the script to deploy TeSLA CE Supervisor
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_supervisor_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for TeSLA CE Supervisor
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _deploy_core_module(self, credentials, module) -> dict:
        """
            Deploy TeSLA CE Core module
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _deploy_dashboard(self) -> dict:
        """
            Deploy TeSLA CE Dashboard
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _deploy_moodle(self, credentials) -> dict:
        """
            Deploy TeSLA CE Moodle
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _deploy_instrument_provider(self, credentials, provider) -> dict:
        """
            Deploy TeSLA CE Instrument provider
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_core_module_script(self, credentials, module) -> SetupOptions:
        """
            Get the script to deploy TeSLA CE Core module
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_dashboard_script(self) -> SetupOptions:
        """
            Get the script to deploy TeSLA CE Dashboard
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_instrument_provider_script(self, module, credentials, provider) -> SetupOptions:
        """
            Get the script to deploy TeSLA CE Instrument provider script
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_moodle_script(self, credentials) -> SetupOptions:
        """
            Get the script to deploy TeSLA CE Instrument provider script
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_dashboard_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for TeSLA CE Dashboard
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_moodle_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for TeSLA CE Moodle
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_instrument_provider_status(self, module) -> ServiceDeploymentInformation:
        """
            Get the deployment information for TeSLA CE Moodle
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def _get_core_module_status(self, module) -> ServiceDeploymentInformation:
        """
            Get the deployment information for TeSLA CE Core module
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def execute_command_inside_container(self, container, command) -> CommandStatus:
        """
            Get the deployment information for TeSLA CE Supervisor
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    def generate_deployment_credentials(self, module: ModuleCode):
        """
            Generate required credentials for a given module
            :param module: Name of the module
        """
        if module.upper() == "LB":
            # No configuration needed
            pass
        elif module.upper() == "DATABASE":
            if self._config.get('DEPLOYMENT_SERVICES') is True:
                if self._config.get('DB_PASSWORD') is None:
                    self._config.set('DB_PASSWORD', self._config.get_uuid())
                if self._config.get('DB_ROOT_PASSWORD') is None:
                    self._config.set('DB_ROOT_PASSWORD', self._config.get_uuid())

        elif module.upper() == "REDIS":
            if self._config.get('DEPLOYMENT_SERVICES') is True:
                if self._config.get('REDIS_PASSWORD') is None:
                    self._config.set('REDIS_PASSWORD', self._config.get_uuid())
        elif module.upper() == "MINIO":
            if self._config.get('DEPLOYMENT_SERVICES') is True:
                if self._config.get('STORAGE_ACCESS_KEY') is None:
                    self._config.set('STORAGE_ACCESS_KEY', self._config.get_uuid())
                if self._config.get('STORAGE_SECRET_KEY') is None:
                    self._config.set('STORAGE_SECRET_KEY', self._config.get_uuid())

        elif module.upper() == "RABBITMQ":
            if self._config.get('DEPLOYMENT_SERVICES') is True:
                if self._config.get('RABBITMQ_ADMIN_USER') is None:
                    self._config.set('RABBITMQ_ADMIN_USER', self._config.get_uuid())
                if self._config.get('RABBITMQ_ADMIN_PASSWORD') is None:
                    self._config.set('RABBITMQ_ADMIN_PASSWORD', self._config.get_uuid())
                if self._config.get('RABBITMQ_ERLANG_COOKIE') is None:
                    self._config.set('RABBITMQ_ERLANG_COOKIE', self._config.get_uuid())

                if self._config.get('CELERY_BROKER_USER') is None:
                    self._config.set('CELERY_BROKER_USER', self._config.get('RABBITMQ_ADMIN_USER'))

                if self._config.get('CELERY_BROKER_PASSWORD') is None:
                    self._config.set('CELERY_BROKER_PASSWORD', self._config.get('RABBITMQ_ADMIN_PASSWORD'))

        elif module.upper() == "VAULT":
            # No configuration needed
            pass
        elif module.upper() == "SUPERVISOR":
            # Check if admin password exists or must be created
            if self._config.get('SUPERVISOR_ADMIN_PASSWORD') is None:
                self._config.set('SUPERVISOR_ADMIN_PASSWORD', User.objects.make_random_password())

            if self._config.get('SUPERVISOR_ADMIN_EMAIL') is None:
                self._config.set('SUPERVISOR_ADMIN_EMAIL', self._config.get('TESLA_ADMIN_MAIL'))

            if self._config.get('SUPERVISOR_SECRET') is None:
                self._config.set('SUPERVISOR_SECRET', self._config.get_uuid())

    def get_status(self, module: ModuleCode) -> ServiceDeploymentInformation:
        """
            Get module status
            :param module: Name of the module
        """

        if module.upper() == "LB":
            return self._get_lb_status()
        elif module.upper() == "DATABASE":
            return self._get_database_status()
        elif module.upper() == "REDIS":
            return self._get_redis_status()
        elif module.upper() == "MINIO":
            return self._get_minio_status()
        elif module.upper() == "RABBITMQ":
            return self._get_rabbitmq_status()
        elif module.upper() == "VAULT":
            return self._get_vault_status()
        elif module.upper() == "SUPERVISOR":
            return self._get_supervisor_status()
        elif module.upper() == "DASHBOARD":
            return self._get_dashboard_status()
        elif module.upper() == "MOODLE":
            return self._get_moodle_status()
        elif module.upper() in ["WORKER-ALL", "WORKER-ENROLMENT", "WORKER-ENROLMENT-STORAGE",
                                "WORKER-ENROLMENT-VALIDATION", "WORKER-VERIFICATION", "WORKER-ALERTS",
                                "WORKER-REPORTING", "API", "LAPI", "BEAT"]:
            return self._get_core_module_status(module.upper())
        elif module.upper() in ["TKS", "TPT", "TFR"]:
            return self._get_instrument_provider_status(module.upper())

        raise TeslaDeployException(INVALID_MODULE_MESSAGE.format(module))

    def get_script(self, module: ModuleCode, credentials=None, provider=None) -> SetupOptions:
        """
            Get deployment script
            :param credentials:
            :param module: Name of the module
        """
        self.generate_deployment_credentials(module=module)

        if module.upper() == "LB":
            return self._get_lb_script()
        elif module.upper() == "DATABASE":
            return self._get_database_script()
        elif module.upper() == "REDIS":
            return self._get_redis_script()
        elif module.upper() == "MINIO":
            return self._get_minio_script()
        elif module.upper() == "RABBITMQ":
            return self._get_rabbitmq_script()
        elif module.upper() == "VAULT":
            return self._get_vault_script()
        elif module.upper() == "SUPERVISOR":
            return self._get_supervisor_script()
        elif module.upper() == "DASHBOARD":
            return self._get_dashboard_script()
        elif module.upper() in ["WORKER-ALL", "WORKER-ENROLMENT", "WORKER-ENROLMENT-STORAGE",
                                "WORKER-ENROLMENT-VALIDATION", "WORKER-VERIFICATION", "WORKER-ALERTS",
                                "WORKER-REPORTING", "API", "LAPI", "BEAT"]:
            return self._get_core_module_script(credentials, module.upper())
        elif module.upper() in ["TFR", "TPT", "TKS"]:
            return self._get_instrument_provider_script(module.upper(), credentials, provider)
        elif module.upper() == "MOODLE":
            return self._get_moodle_script(credentials)



        raise TeslaDeployException(INVALID_MODULE_MESSAGE.format(module))

    def deploy(self, module: ModuleCode, credentials: dict = {}, provider: dict = {}) -> dict:
        """
            Deploy a module
            :param credentials: dict
            :param module: Name of the module
        """
        self.generate_deployment_credentials(module=module)

        if module.upper() == "LB":
            return self._deploy_lb()
        elif module.upper() == "DATABASE":
            return self._deploy_database()
        elif module.upper() == "REDIS":
            return self._deploy_redis()
        elif module.upper() == "MINIO":
            return self._deploy_minio()
        elif module.upper() == "RABBITMQ":
            return self._deploy_rabbitmq()
        elif module.upper() == "VAULT":
            return self._deploy_vault()
        elif module.upper() == "SUPERVISOR":
            return self._deploy_supervisor()
        elif module.upper() in ["WORKER-ALL", "WORKER-ENROLMENT", "WORKER-ENROLMENT-STORAGE",
                                "WORKER-ENROLMENT-VALIDATION", "WORKER-VERIFICATION", "WORKER-ALERTS",
                                "WORKER-REPORTING", "API", "BEAT", "LAPI"]:
            return self._deploy_core_module(credentials, module.upper())
        elif module.upper() == "DASHBOARD":
            return self._deploy_dashboard()
        elif module.upper() == "MOODLE":
            return self._deploy_moodle(credentials)
        elif module.upper() in ["TKS", "TPT", "TFR"]:
            return self._deploy_instrument_provider(credentials, provider)

        raise TeslaDeployException(INVALID_MODULE_MESSAGE.format(module))

    def remove(self, module: ModuleCode, provider=None) -> dict:
        """
            Remove deployed module
            :param module: Name of the module
        """
        if module.upper() == "LB":
            return self._remove_lb()
        elif module.upper() == "DATABASE":
            return self._remove_database()
        elif module.upper() == "REDIS":
            return self._remove_redis()
        elif module.upper() == "MINIO":
            return self._remove_minio()
        elif module.upper() == "RABBITMQ":
            return self._remove_rabbitmq()
        elif module.upper() == "VAULT":
            return self._remove_vault()
        elif module.upper() == "SUPERVISOR":
            return self._remove_supervisor()
        elif module.upper() == "DASHBOARD":
            return self._remove_dashboard()
        elif module.upper() in ["WORKER-ALL", "WORKER-ENROLMENT", "WORKER-ENROLMENT-STORAGE",
                                "WORKER-ENROLMENT-VALIDATION", "WORKER-VERIFICATION", "WORKER-ALERTS",
                                "WORKER-REPORTING", "API", "BEAT", "LAPI"]:
            return self._remove_core_module(module.upper())
        elif module.upper() in ["TKS", "TPT", "TFR"]:
            return self._remove_instrument_provider(provider)
        elif module.upper() == "MOODLE":
            return self._remove_moodle()


        raise TeslaDeployException(INVALID_MODULE_MESSAGE.format(module))
