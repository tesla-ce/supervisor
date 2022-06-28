import abc
import typing

from ..setup_options import SetupOptions
from ..tesla.conf import Config
from ..models.check import ServiceDeploymentInformation, ConnectionStatus


NOT_IMPLEMENTED_MESSAGE = 'Method not implemented'


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
