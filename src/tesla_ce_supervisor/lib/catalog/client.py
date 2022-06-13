import typing
from django.conf import settings

from .consul_catalog import ConsulCatalog, Config
from ..models.check import ServiceCatalogInformation


class CatalogClient:

    def __init__(self, config: typing.Optional[Config] = None) -> None:
        self._client = None
        self._config = config

        if settings.CATALOG_SERVICE == "CONSUL":
            self._client = ConsulCatalog(config)

        # todo: add swarm support

        assert self._client is not None

    def get_services(self):
        return self._client.get_services()

    def get_database_status(self) -> ServiceCatalogInformation:
        return self._client.get_database_status()

    def get_lb_status(self) -> ServiceCatalogInformation:
        return self._client.get_lb_status()

    def get_minio_status(self) -> ServiceCatalogInformation:
        return self._client.get_minio_status()

    def get_rabbitmq_status(self) -> ServiceCatalogInformation:
        return self._client.get_rabbitmq_status()

    def get_vault_status(self) -> ServiceCatalogInformation:
        return self._client.get_vault_status()

    def get_redis_status(self) -> ServiceCatalogInformation:
        return self._client.get_redis_status()
