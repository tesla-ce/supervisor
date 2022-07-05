import abc
import typing

from django.contrib.auth.models import User

from .exceptions import TeslaDeployException
from ..setup_options import SetupOptions
from ..tesla.conf import Config
from ..models.check import ServiceDeploymentInformation, ConnectionStatus

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
    def test_connection(self) -> ConnectionStatus:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def write_scripts(self) -> None:
        """
            Write deployment scripts
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def deploy_lb(self) -> dict:
        """
            Deploy Load Balancer
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def remove_lb(self) -> dict:
        """
            Remove deployed Load Balancer
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_lb_script(self) -> SetupOptions:
        """
            Get the script to deploy Load Balancer
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_lb_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for Load Balancer
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def deploy_vault(self) -> dict:
        """
            Deploy Hashicorp Vault
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def remove_vault(self) -> dict:
        """
            Remove deployed Vault
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_vault_script(self) -> SetupOptions:
        """
            Get the script to deploy Hashicorp Vault
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_vault_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for Vault
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def deploy_minio(self) -> dict:
        """
            Deploy MinIO
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def remove_minio(self) -> dict:
        """
            Remove deployed MinIO
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_minio_script(self) -> SetupOptions:
        """
            Get the script to deploy MinIO
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_minio_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for MinIO
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def deploy_redis(self) -> dict:
        """
            Deploy Redis
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def remove_redis(self) -> dict:
        """
            Remove deployed Redis
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_redis_script(self) -> SetupOptions:
        """
            Get the script to deploy Redis
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_redis_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for Redis
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def deploy_database(self) -> dict:
        """
            Deploy Database
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def remove_database(self) -> dict:
        """
            Remove deployed Database
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_database_script(self) -> SetupOptions:
        """
            Get the script to deploy Database
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_database_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for Database
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def deploy_rabbitmq(self) -> dict:
        """
            Deploy RabbitMQ
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def remove_rabbitmq(self) -> dict:
        """
            Remove deployed RabbitMQ
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_rabbitmq_script(self) -> SetupOptions:
        """
            Get the script to deploy RabbitMQ
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_rabbitmq_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for RabbitMQ
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @staticmethod
    def _remove_empty_lines(text):
        return '\n'.join([line for line in text.split('\n') if line.strip()])

    @abc.abstractmethod
    def deploy_supervisor(self) -> dict:
        """
            Deploy TeSLA CE Supervisor
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def remove_supervisor(self) -> dict:
        """
            Remove deployed TeSLA CE Supervisor
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_supervisor_script(self) -> SetupOptions:
        """
            Get the script to deploy TeSLA CE Supervisor
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_supervisor_status(self) -> ServiceDeploymentInformation:
        """
            Get the deployment information for TeSLA CE Supervisor
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    def genereate_deployment_credentials(self, module: ModuleCode):
        """
            Generate required credentials for a given module
            :param module: Name of the module
        """
        if module.upper() == "LB":
            # No configuration needed
            pass
        elif module.upper() == "DATABASE":
            pass
        elif module.upper() == "REDIS":
            pass
        elif module.upper() == "MINIO":
            pass
        elif module.upper() == "RABBITMQ":
            pass
        elif module.upper() == "VAULT":
            # No configuration needed
            pass
        elif module.upper() == "SUPERVISOR":
            # Check if admin password exists or must be created
            if self._config.get('SUPERVISOR_ADMIN_PASSWORD') is None:
                self._config.set('SUPERVISOR_ADMIN_PASSWORD', User.objects.make_random_password())

    def get_status(self, module: ModuleCode) -> ServiceDeploymentInformation:
        """
            Get module status
            :param module: Name of the module
        """
        if module.upper() == "LB":
            return self.get_lb_status()
        elif module.upper() == "DATABASE":
            return self.get_database_status()
        elif module.upper() == "REDIS":
            return self.get_redis_status()
        elif module.upper() == "MINIO":
            return self.get_minio_status()
        elif module.upper() == "RABBITMQ":
            return self.get_rabbitmq_status()
        elif module.upper() == "VAULT":
            return self.get_vault_status()
        elif module.upper() == "SUPERVISOR":
            return self.get_supervisor_status()

        raise TeslaDeployException(INVALID_MODULE_MESSAGE.format(module))

    def get_script(self, module: ModuleCode) -> SetupOptions:
        """
            Get deployment script
            :param module: Name of the module
        """
        if module.upper() == "LB":
            return self.get_lb_script()
        elif module.upper() == "DATABASE":
            return self.get_database_script()
        elif module.upper() == "REDIS":
            return self.get_redis_script()
        elif module.upper() == "MINIO":
            return self.get_minio_script()
        elif module.upper() == "RABBITMQ":
            return self.get_rabbitmq_script()
        elif module.upper() == "VAULT":
            return self.get_vault_script()
        elif module.upper() == "SUPERVISOR":
            return self.get_supervisor_script()

        raise TeslaDeployException(INVALID_MODULE_MESSAGE.format(module))

    def deploy(self, module: ModuleCode) -> dict:
        """
            Deploy a module
            :param module: Name of the module
        """
        if module.upper() == "LB":
            return self.deploy_lb()
        elif module.upper() == "DATABASE":
            return self.deploy_database()
        elif module.upper() == "REDIS":
            return self.deploy_redis()
        elif module.upper() == "MINIO":
            return self.deploy_minio()
        elif module.upper() == "RABBITMQ":
            return self.deploy_rabbitmq()
        elif module.upper() == "VAULT":
            return self.deploy_vault()
        elif module.upper() == "SUPERVISOR":
            return self.deploy_supervisor()

        raise TeslaDeployException(INVALID_MODULE_MESSAGE.format(module))

    def remove(self, module: ModuleCode) -> dict:
        """
            Remove deployed module
            :param module: Name of the module
        """
        if module.upper() == "LB":
            return self.remove_lb()
        elif module.upper() == "DATABASE":
            return self.remove_database()
        elif module.upper() == "REDIS":
            return self.remove_redis()
        elif module.upper() == "MINIO":
            return self.remove_minio()
        elif module.upper() == "RABBITMQ":
            return self.remove_rabbitmq()
        elif module.upper() == "VAULT":
            return self.remove_vault()
        elif module.upper() == "SUPERVISOR":
            return self.remove_supervisor()

        raise TeslaDeployException(INVALID_MODULE_MESSAGE.format(module))
