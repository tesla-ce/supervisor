from typing import Optional

from .nomad_client import NomadDeploy
from .swarm_client import SwarmDeploy


class DeployClient:
    """
        Deployment Client, used to generate and optionally run deployment scripts
    """

    def __init__(self, target: str, use_terraform: Optional[bool] = False):
        self._client = None

        if target.upper() == "NOMAD":
            self._client = NomadDeploy(use_terraform)
        elif target.upper() == "SWARM":
            self._client = SwarmDeploy(use_terraform)

        assert self._client is not None
