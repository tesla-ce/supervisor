from .catalog import CatalogClient


class SupervisorClient:

    def __init__(self):

        self._catalog = CatalogClient()

    def get_services(self):
        return self._catalog.get_services()
