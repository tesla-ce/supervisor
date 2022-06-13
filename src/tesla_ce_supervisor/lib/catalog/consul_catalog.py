import urllib

import consul
import typing

from django.conf import settings

from .base import BaseCatalog, ServiceCatalogInformation, Config


class ConsulCatalog(BaseCatalog):

    def __init__(self, config: typing.Optional[Config] = None) -> None:
        super().__init__(config)

        self._client = consul.Consul(host=settings.CONSUL_HOST,
                                     port=settings.CONSUL_PORT,
                                     scheme=settings.CONSUL_SCHEME,
                                     verify=settings.CONSUL_VERIFY,
                                     cert=settings.CONSUL_CERT
                                     )

    def _merge_status_data(self, name: str,
                           stats: typing.List[ServiceCatalogInformation]) -> ServiceCatalogInformation:
        status = ServiceCatalogInformation(name, 'consul')
        status.instances_total = 0
        status.instances_healthy = 0
        status.services = []
        status.info = {}

        for stat in stats:
            status.instances_total += stat.instances_total
            status.instances_healthy += stat.instances_healthy
            status.services += stat.services
            status.info[stat.name] = stat.info[stat.name]

        return status

    def get_services(self) -> typing.List[ServiceCatalogInformation]:
        index, services = self._client.catalog.services()
        srv_list = []
        for srv in services:
            srv_list.append(self.get_service_status(srv))
        return srv_list

    def get_service_status(self, name: str) -> ServiceCatalogInformation:
        service_health = self._client.health.service(name)

        total_instances = 0
        healthy_instances = 0
        for instance in service_health[1]:
            total_instances += 1
            pass_all = True
            for check in instance['Checks']:
                if check['Status'] != 'passing':
                    pass_all = False
            if pass_all:
                healthy_instances += 1

        status = ServiceCatalogInformation(name, 'consul')
        status.instances_total = total_instances
        status.instances_healthy = healthy_instances
        status.services.append({
            'name': name, 'total_instances': total_instances, 'healthy_instances': healthy_instances})
        status.info = {name: service_health}
        return status

    def get_lb_status(self) -> ServiceCatalogInformation:
        return self._merge_status_data('traefik',
                                       [self.get_service_status('traefik-http'),
                                       self.get_service_status('traefik-https')])

    def get_database_status(self) -> ServiceCatalogInformation:
        return self._merge_status_data('database',
                                       [self.get_service_status('{}-server'.format(self._config.get('DB_ENGINE')))])

    def register_database(self):
        self._client.catalog.register(
            node='mysql-server',
            address=self._config.get('DB_HOST'),
            service={
                "Service": "mysql-server",
                "Tags": [
                    "tesla-ce",
                    "external",
                    "service",
                    "mysql",
                ],
                "Port": self._config.get('DB_PORT')
            })

    def deregister_database(self):
        self._client.catalog.deregister(node='mysql-server')

    def get_vault_status(self) -> ServiceCatalogInformation:
        return self._merge_status_data('database',
                                       [self.get_service_status('vault')])

    def register_vault(self):
        port = 8200  # TODO: Extract from Vault URL
        self._client.catalog.register(
            node='vault',
            address=self._config.get('VAULT_URL'),
            service={
                "Service": "mysql-server",
                "Tags": [
                    "tesla-ce",
                    "external",
                    "service",
                    "vault",
                ],
                "Port": port
            })

    def deregister_vault(self):
        self._client.catalog.deregister(node='vault')

    def get_redis_status(self) -> ServiceCatalogInformation:
        return self._merge_status_data('redis',
                                       [self.get_service_status('redis')])

    def get_rabbitmq_status(self) -> ServiceCatalogInformation:
        return self._merge_status_data('rabbitmq',
                                       [self.get_service_status('rabbitmq'),
                                        self.get_service_status('rabbitmq-management')])

    def get_minio_status(self) -> ServiceCatalogInformation:
        return self._merge_status_data('minio',
                                       [self.get_service_status('minio-api'),
                                        self.get_service_status('minio-console')])
