import docker
import typing

from django.conf import settings

from .base import BaseCatalog, ServiceCatalogInformation, Config
from ..models.check import ConnectionStatus

NOT_IMPLEMENTED_MESSAGE = 'Method not implemented'

class SwarmCatalog(BaseCatalog):

    def __init__(self, config: typing.Optional[Config] = None) -> None:
        super().__init__(config)

        self.config = config
        self._client = docker.DockerClient(base_url=self.config.get('swarm_base_url'))

        assert self._client is not None

    def get_services(self) -> typing.List[ServiceCatalogInformation]:
        return []

    def get_service_status(self, name: str) -> ServiceCatalogInformation:
        status = ServiceCatalogInformation(name, 'swarm')
        service = None
        total_instances = 0
        healthy_instances = 0
        service_health = None
        try:
            service_id = '{}_{}'.format(self.config.get('swarm_service_prefix'), name)
            service = self._client.services.get(service_id)
            total_instances = service.attrs['Spec']['Mode']['Replicated']['Replicas']
            healthy_instances = len(service.tasks(filters={'desired-state': 'RUNNING'}))

        except docker.errors.DockerException as err:
            pass

        status = ServiceCatalogInformation(name, 'swarm')
        status.instances_total = total_instances
        status.instances_healthy = healthy_instances
        status.services.append({
            'name': name, 'total_instances': total_instances, 'healthy_instances': healthy_instances})
        status.info = {name: service_health}

        return status

    def get_lb_status(self) -> ServiceCatalogInformation:
        return self.get_service_status('traefik')

    def get_database_status(self) -> ServiceCatalogInformation:
        return self.get_service_status('database')

    def register_database(self) -> ServiceCatalogInformation:
        # todo:
        pass

    def deregister_database(self) -> ServiceCatalogInformation:
        pass

    def get_vault_status(self) -> ServiceCatalogInformation:
        return self.get_service_status('vault')

    def get_redis_status(self) -> ServiceCatalogInformation:
        return self.get_service_status('redis')

    def get_rabbitmq_status(self) -> ServiceCatalogInformation:
        return self.get_service_status('rabbitmq')

    def get_minio_status(self) -> ServiceCatalogInformation:
        return self.get_service_status('minio')

    def get_supervisor_status(self) -> ServiceCatalogInformation:
        return self.get_service_status('supervisor')
