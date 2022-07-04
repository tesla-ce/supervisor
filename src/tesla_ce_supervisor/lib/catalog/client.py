import typing
from django.conf import settings

from .consul_catalog import ConsulCatalog, Config
from .swarm_catalog import SwarmCatalog
from ..models.check import ServiceCatalogInformation, ConnectionStatus


class CatalogClient:

    def __init__(self, config: typing.Optional[Config] = None) -> None:
        self._client = None
        self._config = config

        catalog_service = self._config.get('deployment_catalog_system')
        if catalog_service.upper() == "CONSUL":
            self._client = ConsulCatalog(config)

        if catalog_service.upper() == "SWARM":
            self._client = SwarmCatalog(config)

        assert self._client is not None

    def check_connection(self) -> ConnectionStatus:
        return self._client.test_connection()

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

    def get_supervisor_status(self) -> ServiceCatalogInformation:
        return self._client.get_supervisor_status()
