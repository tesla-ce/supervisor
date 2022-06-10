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
