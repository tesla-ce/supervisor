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
        self._tesla.get_config().set('TESLA_DOMAIN', 'nomad.demo.tesla-ce.eu')
        self._tesla.get_config().set('TESLA_ADMIN_MAIL', 'admin@nomad.demo.tesla-ce.eu')
        self._tesla.get_config().set('STORAGE_REGION', 'eu-west-1')
        self._tesla.get_config().set('STORAGE_ACCESS_KEY', 'AKIAIOSFODNN7EXAMPLE')
        self._tesla.get_config().set('STORAGE_SECRET_KEY', 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY')
        self._tesla.get_config().set('DB_ENGINE', 'mysql')
        self._tesla.get_config().set('DB_ROOT_PASSWORD', '.-.-#!/MyVerySecurePassword')
        self._tesla.get_config().set('DB_PASSWORD', 'MyVerySecurePasswordForUser321!--..-')
        self._tesla.get_config().set('DB_USER', 'tesla')
        self._tesla.get_config().set('DB_NAME', 'tesla')
        self._tesla.get_config().set('RABBITMQ_ADMIN_USER', 'ebbe970e-46f0-4654-bd2d-7e8c0724aacc')
        self._tesla.get_config().set('RABBITMQ_ADMIN_PASSWORD', 'b52a7ba8-9cd3-4e69-a11e-4d0f66465937')
        self._tesla.get_config().set('RABBITMQ_ERLANG_COOKIE', 'ee77b359-57c0-4037-ae70-a688f178f35f')
        self._tesla.get_config().set('REDIS_PASSWORD', '.-.-#!/MyVerySecurePassword')

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
