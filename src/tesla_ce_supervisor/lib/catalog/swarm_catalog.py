import docker
import typing

from django.conf import settings

from .base import BaseCatalog, ServiceCatalogInformation


class SwarmCatalog(BaseCatalog):

    def __init__(self):
        super().__init__()
        self._client = None

    def get_services(self) -> typing.List[ServiceCatalogInformation]:
        return []

    def get_service_status(self, name: str) -> ServiceCatalogInformation:
        status = ServiceCatalogInformation(name)
        return status

    def get_lb_status(self) -> ServiceCatalogInformation:
        return self.get_service_status('traefik')
