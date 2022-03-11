import abc
import typing


class Service:
    name: str
    instances: int
    healthy: int


class BaseCatalog(abc.ABC):

    filter_tag = 'tesla-ce'

    @abc.abstractmethod
    def get_services(self) -> typing.List[Service]:
        pass

