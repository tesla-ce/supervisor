import docker
import typing
import os
import base64
from django.conf import settings

from .base import BaseCatalog, ServiceCatalogInformation, Config
from ..models.check import ConnectionStatus

NOT_IMPLEMENTED_MESSAGE = 'Method not implemented'

class SwarmCatalog(BaseCatalog):
    _client = None

    def __init__(self, config: typing.Optional[Config] = None) -> None:
        super().__init__(config)
        self.config = config

    @property
    def client(self):
        if self._client is None:
            self.config.get('swarm_base_url')

            tls_config = None

            if self.config.get('swarm_client_key') is not None and self.config.get('swarm_client_cert') is not None and \
                    self.config.get('swarm_specific_ca_cert') is not None:

                client_key_file = os.path.join(settings.DATA_DIRECTORY, 'client_key.pem')
                with open(client_key_file, 'w') as file:
                    content = base64.b64decode(self.config.get('swarm_client_key')).decode('utf8')
                    file.write(content)
                    file.close()

                client_cert_file = os.path.join(settings.DATA_DIRECTORY, 'client_cert.pem')
                with open(client_cert_file, 'w') as file:
                    content = base64.b64decode(self.config.get('swarm_client_cert')).decode('utf8')
                    file.write(content)
                    file.close()

                client_ca_file = os.path.join(settings.DATA_DIRECTORY, 'client_ca.pem')
                with open(client_ca_file, 'w') as file:
                    content = base64.b64decode(self.config.get('swarm_specific_ca_cert')).decode('utf8')
                    file.write(content)
                    file.close()

                tls_config = docker.tls.TLSConfig(
                    client_cert=(client_cert_file, client_key_file), ca_cert=client_ca_file
                )

            self._client = docker.DockerClient(base_url=self.config.get('swarm_base_url'), tls=tls_config)

        assert self._client is not None

        return self._client

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
            service = self.client.services.get(service_id)
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

    def get_api_status(self) -> ServiceCatalogInformation:
        return self.get_service_status('api')
