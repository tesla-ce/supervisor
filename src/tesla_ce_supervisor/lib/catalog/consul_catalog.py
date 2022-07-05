import urllib
import os
import consul
import typing

from django.conf import settings

from .base import BaseCatalog, ServiceCatalogInformation, Config
from ..models.check import ConnectionStatus


class ConsulConfig:
    """
        Consul configuration
    """
    # Nomad server URL
    consul_host: str = '127.0.0.1'

    # Consul server port
    consul_port: int = 8500

    # Consul connection scheme
    consul_scheme: str = 'http'

    # Authentication
    consul_auth: typing.Optional[typing.Union[typing.Literal["ACL"], typing.Literal["CERT"]]] = None

    # Consul SecretID of an ACL token for authentication
    consul_token: typing.Optional[str] = None

    # Verify Server identity
    consul_verify: bool = True

    def __init__(self, config, consul_host: typing.Optional[str] = None,
                 consul_port: typing.Optional[int] = None,
                 consul_scheme: typing.Optional[typing.List[str]] = None,
                 consul_auth: typing.Optional[typing.Union[typing.Literal["ACL"], typing.Literal["CERT"]]] = None,
                 consul_token: typing.Optional[str] = None,
                 consul_verify: typing.Optional[bool] = None,
                 consul_cert: typing.Optional[str] = None,
                 ) -> None:

        # Consul configuration
        self.consul_auth = self._set_value(
            config, consul_auth
        )
        self.consul_host = self._set_value(config, consul_host, 'CONSUL_HOST', 'CONSUL_HOST')
        self.consul_port = self._set_value(config, consul_port, 'CONSUL_PORT', 'CONSUL_PORT')
        self.consul_scheme = self._set_value(config, consul_scheme, 'CONSUL_SCHEME', 'CONSUL_SCHEME')
        self.consul_verify = self._set_value(config, consul_verify, 'CONSUL_VERIFY', 'CONSUL_VERIFY')
        self.consul_token = self._set_value(config, consul_token, 'CONSUL_TOKEN', 'CONSUL_ACL_TOKEN')

        # self.consul_cert = self._set_value(config, consul_cert, 'CONSUL_CERT', 'CONSUL_CERT')

    @staticmethod
    def _set_value(config, parameter, env_key=None, conf_key=None, default=None):
        if parameter is not None:
            return parameter
        default_value = None
        if conf_key is not None:
            default_value = config.get(conf_key)
        if env_key is not None:
            ret_val = os.getenv(env_key, default_value)
        else:
            ret_val = default_value
        if ret_val is None:
            ret_val = default
        return ret_val


class ConsulCatalog(BaseCatalog):

    def __init__(self, config: typing.Optional[Config] = None, consul_conf: typing.Optional[ConsulConfig] = None) -> None:
        super().__init__(config)

        self.consul_conf = consul_conf
        if self.consul_conf is None:
            self.consul_conf = ConsulConfig(config)
        if self.consul_conf.consul_auth is None:
            self._client = consul.Consul(
                host=self.consul_conf.consul_host,
                port=self.consul_conf.consul_port,
                scheme=self.consul_conf.consul_scheme,
                verify=self.consul_conf.consul_verify,
            )
        elif self.consul_conf.consul_auth == "ACL":
            self._client = consul.Consul(
                host=self.consul_conf.consul_host,
                port=self.consul_conf.consul_port,
                scheme=self.consul_conf.consul_scheme,
                verify=self.consul_conf.consul_verify,
                token=self.consul_conf.consul_token,
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

    def get_supervisor_status(self) -> ServiceCatalogInformation:
        return self._merge_status_data('supervisor',
                                       [self.get_service_status('supervisor'),])
