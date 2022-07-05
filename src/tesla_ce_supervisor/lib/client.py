import typing
import socket
from django.conf import settings
from django.contrib.auth import get_user_model

from .catalog import CatalogClient
from .tesla import TeslaClient
from .deploy import DeployClient
from .setup import SetupClient

from .models.check import ServiceStatus, ConnectionStatus


class SupervisorClient:

    def __init__(self):
        self._tesla = TeslaClient()
        self._tesla.get_config_path()
        self._tesla.load_configuration()
        self._catalog = CatalogClient(self._tesla.get_config())
        self._deploy = DeployClient(self._tesla.get_config())

    @property
    def tesla(self):
        return self._tesla

    @property
    def catalog(self):
        return self._catalog

    @property
    def deploy(self):
        return self._deploy

    def get_services(self):
        return self._catalog.get_services()

    def configuration_exists(self):
        return self._tesla.configuration_exists()

    def check_configuration(self):
        return self._tesla.check_configuration()

    def export_configuration(self):
        return self._tesla.export_configuration()

    def load_configuration(self):
        return self._tesla.load_configuration()

    def get_config_path(self):
        return self._tesla.get_config_path()

    def check_services(self):

        status = {
            # Check Database
            'db': self.check_database(),
            # Check Vault
            'vault': self.check_vault(),
            # Check MinIO
            'minio': self.check_minio(),
            # Check Redis
            'redis': self.check_redis(),
            # Check RabbitMQ
            'rabbitmq': self.check_rabbitmq(),
        }
        all_ok = True
        errors = []
        for srv in status:
            if not status[srv].is_valid():
                all_ok = False
                errors.append(status[srv].to_json())

        return {
            'valid': all_ok,
            'status': status,
            'errors': errors
        }

    def auto_deploy(self):
        # load config from env
        # write config file
        # deploy LB?
        # deploy services?
        # setup vault
        # deploy core
        # deploy dashboard

        # deploy VLE?

        # deploy providers? info in env variable.

        # todo: implement this with exit()
        # todo: write file log
        pass

    def get_vault_configuration(self) -> dict:
        """
            Get the list of Vault configuration files to be exported or executed
            :return: Dictionary with all required files and content for each file
        """
        return {
            'tesla-ce-policies.hcl': self._tesla.get_vault_policies(),
        }

    def setup_vault(self) -> None:
        """
            Run Vault configuration
        """
        pass

    def get_deployer(self,
                     target: typing.Optional[typing.Union[typing.Literal["NOMAD"], typing.Literal["SWARM"]]] = None
                     ) -> DeployClient:
        """
            Create a deployer instance using current configuration
            :param target: The target system (Nomad or Swarm)
            :return: Deployer instance
        """
        self._tesla.get_config_path()
        self._tesla.load_configuration()
        return DeployClient(self._tesla.get_config(), target)

    def get_setup(self):
        """
            Create a setup instance using current configuration
            :return: SetupClient instance
        """
        return SetupClient(self._tesla.get_config())

    def check_dns(self, hostname: typing.Optional[str] = None) -> dict:
        """
            Check if a hostname is registered can be resolved.
            :param hostname: The hostname to test. If not provided, all required hostnames are checked.
            :return: Resolution information
        """
        if hostname is None:
            # Get domain
            base_domain = self._tesla.get_config().get('TESLA_DOMAIN')
            if base_domain is None:
                return {}
            # Return values for all required hostnames
            ret_val = {
                base_domain: self.check_dns(hostname=base_domain),
            }
            # If services are deployed, check services domains
            if self._tesla.get_config().get('DEPLOYMENT_SERVICES'):
                ret_val[f'vault.{base_domain}'] = self.check_dns(hostname=f'vault.{base_domain}')
                ret_val[f'storage.{base_domain}'] = self.check_dns(hostname=f'storage.{base_domain}')
                ret_val[f'rabbitmq.{base_domain}'] = self.check_dns(hostname=f'rabbitmq.{base_domain}')
        else:
            try:
                ip = socket.gethostbyname(hostname)
                ret_val = {
                    'valid': True,
                    'hostname': hostname,
                    'ip': ip,
                    'error': None
                }
            except socket.gaierror as err:
                ret_val = {
                    'valid': False,
                    'hostname': hostname,
                    'ip': None,
                    'error': err.__str__()
                }

        return ret_val

    def check_lb(self) -> ServiceStatus:
        """
            Check deployment status of the load balancer
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_lb_status(),
            self._catalog.get_lb_status()
        )

        return status

    def check_database(self) -> ServiceStatus:
        """
            Check deployment status of the database
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_database_status(),
            self._catalog.get_database_status()
        )

        return status

    def check_minio(self) -> ServiceStatus:
        """
            Check deployment status of MinIO
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_minio_status(),
            self._catalog.get_minio_status()
        )

        return status

    def check_redis(self) -> ServiceStatus:
        """
            Check deployment status of Redis
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_redis_status(),
            self._catalog.get_redis_status()
        )

        return status

    def check_rabbitmq(self) -> ServiceStatus:
        """
            Check deployment status of RabbitMQ
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_rabbitmq_status(),
            self._catalog.get_rabbitmq_status()
        )

        return status

    def check_vault(self) -> ServiceStatus:
        """
            Check deployment status of Vault
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_vault_status(),
            self._catalog.get_vault_status()
        )

        return status

    def check_supervisor(self) -> ServiceStatus:
        """
            Check deployment status of TeSLA CE Supervisor
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_supervisor_status(),
            self._catalog.get_supervisor_status()
        )

        return status


    def check_connection(self, module: str) -> ConnectionStatus:
        """
            Check connection status of module
            :return: ConnectionStatus
        """
        if module.upper() == 'SWARM':
            status = SwarmDeployer(config=self.tesla.get_config()).check_connection(module)

        elif module.upper() == 'NOMAD':
            status = NomadDeployer(config=self.tesla.get_config()).check_connection(module)

        elif module.upper() == 'CONSUL':
            status = ConsulCatalog(config=self.tesla.get_config()).check_connection(module)

        return status
