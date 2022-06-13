from typing import Optional
from django.conf import settings

from .consul_catalog import ConsulCatalog
from ..models.check import ServiceCatalogInformation


class CatalogClient:

    def __init__(self):
        self._client = None

        if settings.CATALOG_SERVICE == "CONSUL":
            self._client = ConsulCatalog()

        # todo: add swarm support

        assert self._client is not None

    def get_services(self):
        return self._client.get_services()

    def get_db_status(self) -> ServiceCatalogInformation:
        # todo: implement
        pass

    def get_lb_status(self) -> ServiceCatalogInformation:
        return self._client.get_lb_status()
