from .catalog import CatalogClient
from .tesla import TeslaClient


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
        return {
            'tesla-ce-policies.hcl': self._tesla.get_vault_policies(),
        }

    def setup_vault(self) -> None:
        """
            Run Vault configuration
        """
        pass
