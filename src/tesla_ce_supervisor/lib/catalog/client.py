from django.conf import settings

from .consul_catalog import ConsulCatalog


class CatalogClient:

    def __init__(self):
        self._client = None

        if settings.CATALOG_SERVICE == "CONSUL":
            self._client = ConsulCatalog()

        assert self._client is not None

    def get_services(self):
        return self._client.get_services()
