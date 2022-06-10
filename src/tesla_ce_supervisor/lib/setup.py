import typing
from .deploy import DeployClient


class SetupOptions:
    require_files: bool = False
    command: typing.List[str] = []
    files: dict = {}

    def get_zip(self):
        # zip files
        pass

    def to_json(self):
        pass


class Setup:
    config = None

    def __init__(self, config):
        self.config = config

    def get_deployer(self,
                     target: typing.Optional[typing.Union[typing.Literal["NOMAD"], typing.Literal["SWARM"]]] = None
                     ) -> DeployClient:
        """
            Create a deployer instance using current configuration
            :param target: The target system (Nomad or Swarm)
            :return: Deployer instance
        """
        return DeployClient(self._tesla.get_config(), target)

    def get_database_setup_options(self) -> SetupOptions:
        # todo: to implement
        return SetupOptions()