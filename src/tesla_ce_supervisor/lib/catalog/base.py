import abc
import typing

from tesla_ce_supervisor.lib.models.check import ServiceCatalogInformation, ConnectionStatus

from ..tesla.conf import Config

NOT_IMPLEMENTED_MESSAGE = 'Method not implemented'


class BaseCatalog(abc.ABC):

    filter_tag = 'tesla-ce'

    def __init__(self, config: typing.Optional[Config] = None) -> None:
        super().__init__()
        self._config = config

    @abc.abstractmethod
    def test_connection(self) -> ConnectionStatus:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_services(self) -> typing.List[ServiceCatalogInformation]:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_service_status(self, name: str) -> ServiceCatalogInformation:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_lb_status(self) -> ServiceCatalogInformation:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_database_status(self) -> ServiceCatalogInformation:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def register_database(self) -> ServiceCatalogInformation:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def deregister_database(self) -> ServiceCatalogInformation:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_vault_status(self) -> ServiceCatalogInformation:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_redis_status(self) -> ServiceCatalogInformation:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_rabbitmq_status(self) -> ServiceCatalogInformation:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_minio_status(self) -> ServiceCatalogInformation:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)



