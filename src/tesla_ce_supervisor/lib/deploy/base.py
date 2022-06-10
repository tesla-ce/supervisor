import abc
import typing

from ..tesla.conf import Config


NOT_IMPLEMENTED_MESSAGE = 'Method not implemented'


class BaseDeploy(abc.ABC):
    """
        Base deployment class. Needs to be extended for each deployment method
    """
    def __init__(self, config: typing.Optional[Config] = None) -> None:
        super().__init__()
        self._config = config

    @abc.abstractmethod
    def write_scripts(self) -> None:
        """
            Write deployment scripts
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def deploy_lb(self) -> None:
        """
            Deploy Load Balancer
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_lb_script(self) -> dict:
        """
            Get the script to deploy Load Balancer
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def deploy_vault(self) -> None:
        """
            Deploy Hashicorp Vault
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_vault_script(self) -> dict:
        """
            Get the script to deploy Hashicorp Vault
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def deploy_minio(self) -> None:
        """
            Deploy MinIO
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_minio_script(self) -> dict:
        """
            Get the script to deploy MinIO
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def deploy_redis(self) -> None:
        """
            Deploy Redis
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_redis_script(self) -> dict:
        """
            Get the script to deploy Redis
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def deploy_database(self) -> None:
        """
            Deploy Database
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_database_script(self) -> dict:
        """
            Get the script to deploy Database
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def deploy_rabbit(self) -> None:
        """
            Deploy RabbitMQ
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_rabbit_script(self) -> dict:
        """
            Get the script to deploy RabbitMQ
        """
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @staticmethod
    def _remove_empty_lines(text):
        return '\n'.join([line for line in text.split('\n') if line.strip()])
