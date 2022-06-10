from typing import Optional, Union, Literal

from .nomad_client import NomadDeploy
from .swarm_client import SwarmDeploy
from ..tesla.conf import Config


class DeployClient:
    """
        Deployment Client, used to generate and optionally run deployment scripts
    """

    def __init__(self, config: Config, target: Optional[Union[Literal["NOMAD"], Literal["SWARM"]]] = None):
        self._client = None

        # Use configuration to set the target
        if target is None:
            # TODO: If target is not provided, use configuration to get it
            target = "NOMAD"

        if target.upper() == "NOMAD":
            self._client = NomadDeploy(config)
        elif target.upper() == "SWARM":
            self._client = SwarmDeploy(config)

        assert self._client is not None

    def deploy_lb(self) -> dict:
        return self._client.deploy_lb()

    def remove_lb(self) -> dict:
        return self._client.remove_lb()

    def deploy_vault(self) -> dict:
        return self._client.deploy_vault()

    def remove_vault(self) -> dict:
        return self._client.remove_vault()

    def deploy_minio(self) -> dict:
        return self._client.deploy_minio()

    def remove_minio(self) -> dict:
        return self._client.remove_minio()

    def deploy_database(self) -> dict:
        return self._client.deploy_database()

    def remove_database(self) -> dict:
        return self._client.remove_database()

    def deploy_rabbitmq(self) -> dict:
        return self._client.deploy_rabbitmq()

    def remove_rabbitmq(self) -> dict:
        return self._client.remove_rabbitmq()

    def deploy_redis(self) -> dict:
        return self._client.deploy_redis()

    def remove_redis(self) -> dict:
        return self._client.remove_redis()
