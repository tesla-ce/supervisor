import typing

from .catalog import CatalogClient
from .tesla import TeslaClient
from .deploy import DeployClient
from .setup import SetupClient


class SupervisorClient:

    def __init__(self):
        self._catalog = CatalogClient()
        self._tesla = TeslaClient()

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
        # TODO: Remove after testing (configuration should be in configuration file or environment)
        self._tesla.get_config().set('NOMAD_ADDR', 'https://console.nomad.demo.tesla-ce.eu')
        self._tesla.get_config().set('NOMAD_REGION', 'global')
        self._tesla.get_config().set('NOMAD_DATACENTERS', ['dc1'])

        # TODO: Remove code after testing
        # Deploy Traefik
        job_data = self.get_deployer().deploy_lb()

        # Remove Traefik
        # job_data = self.get_deployer().remove_lb()

        return {
            'job_data': job_data,
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
