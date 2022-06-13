import consul
import typing

from django.conf import settings

from .base import BaseCatalog, ServiceCatalogInformation


class ConsulCatalog(BaseCatalog):

    def __init__(self):
        super().__init__()

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

