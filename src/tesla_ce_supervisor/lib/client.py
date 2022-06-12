import typing
import socket

from .catalog import CatalogClient
from .tesla import TeslaClient
from .deploy import DeployClient
from .setup import SetupClient


class SupervisorClient:

    def __init__(self):
        self._catalog = CatalogClient()
        self._tesla = TeslaClient()
        self._tesla.get_config_path()
        self._tesla.load_configuration()

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
        # TODO: return hardcoded data

        # check services in catalog (if deploy=True)
        self._catalog.check_database('abc')
        # foreach services check if can connect
        pass

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
        # TODO: Remove code after testing (Set True for deploy and False for removing)
        if True:
            # Deploy Traefik
            job_data = self.get_deployer().deploy_lb()
            # Deploy Vault
            job_data = self.get_deployer().deploy_vault()
            # Deploy MinIO
            job_data = self.get_deployer().deploy_minio()
            # Deploy Database
            job_data = self.get_deployer().deploy_database()
            # Deploy RabbitMQ
            job_data = self.get_deployer().deploy_rabbitmq()
            # Deploy Redis
            job_data = self.get_deployer().deploy_redis()
        else:
            # Remove Traefik
            job_data = self.get_deployer().remove_lb()
            # Remove Vault
            job_data = self.get_deployer().remove_vault()
            # Remove MinIO
            job_data = self.get_deployer().remove_minio()
            # Remove Database
            job_data = self.get_deployer().remove_database()
            # Remove RabbitMQ
            job_data = self.get_deployer().remove_rabbitmq()
            # Remove Redis
            job_data = self.get_deployer().remove_redis()

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

    def check_lb(self) -> dict:
        """
            Check deployment status of the load balancer
            :return: Status information
        """
        return {}
