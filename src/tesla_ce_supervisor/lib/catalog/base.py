import abc
import typing

from tesla_ce_supervisor.lib.models.check import ServiceCatalogInformation

NOT_IMPLEMENTED_MESSAGE = 'Method not implemented'


class BaseCatalog(abc.ABC):

    filter_tag = 'tesla-ce'

    @abc.abstractmethod
    def get_services(self) -> typing.List[ServiceCatalogInformation]:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_service_status(self, name: str) -> ServiceCatalogInformation:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)

    @abc.abstractmethod
    def get_lb_status(self) -> ServiceCatalogInformation:
        raise NotImplementedError(NOT_IMPLEMENTED_MESSAGE)



