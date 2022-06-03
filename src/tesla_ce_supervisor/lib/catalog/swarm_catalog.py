import consul

from django.conf import settings

from .base import BaseCatalog, Service


class SwarmCatalog(BaseCatalog):

    def __init__(self):
        super().__init__()
        # todo: change docker client
        self._client = consul.Consul(host=settings.CONSUL_HOST,
                                     port=settings.CONSUL_PORT,
                                     scheme=settings.CONSUL_SCHEME,
                                     verify=settings.CONSUL_VERIFY,
                                     cert=settings.CONSUL_CERT
                                     )

    def get_services(self):
        # get only tag: tesla-ce services
        index, services = self._client.catalog.services()
        srv_list = []
        for srv in services:
            new_service = Service()
            new_service.name = srv
            srv_list.append(new_service)
        return srv_list

