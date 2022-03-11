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



