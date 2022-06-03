from django.conf import settings

from .consul_catalog import ConsulCatalog
from typing import Optional

class CatalogClient:

    def __init__(self):
        self._client = None

        if settings.CATALOG_SERVICE == "CONSUL":
            self._client = ConsulCatalog()

        # todo: add swarm support

        assert self._client is not None

    def get_services(self):
        return self._client.get_services()

    def check_database(self, a: Optional[int] = None) -> bool:
        # todo: implement
        pass

    def check_lb(self, a: Optional[int] = None) -> dict:
        # todo: implement
        pass