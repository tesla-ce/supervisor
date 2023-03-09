from typing import Optional, Union, Literal

from .base import ModuleCode
from .nomad_client import NomadDeploy
from .swarm_client import SwarmDeploy
from ..tesla.conf import Config
from ..setup_options import SetupOptions
from ..models.check import ServiceDeploymentInformation, ConnectionStatus, CommandStatus


class DeployClient:
    """
        Deployment Client, used to generate and optionally run deployment scripts
    """

    def __init__(self, config: Config, target: Optional[Union[Literal["NOMAD"], Literal["SWARM"]]] = None):
        self._client = None

        # Use configuration to set the target
        if target is None:
            target = config.get('deployment_orchestrator')

        if target.upper() == "NOMAD":
            self._client = NomadDeploy(config)
        elif target.upper() == "SWARM":
            self._client = SwarmDeploy(config)

        assert self._client is not None

    def check_connection(self) -> ConnectionStatus:
        return self._client.test_connection()

    def deploy_lb(self) -> dict:
        return self._client.deploy_lb()

    def remove_lb(self) -> dict:
        return self._client.remove_lb()

    def get_lb_script(self) -> SetupOptions:
        return self._client.get_lb_script()

    def get_lb_status(self) -> ServiceDeploymentInformation:
        return self._client.get_lb_status()

    def deploy_vault(self) -> dict:
        return self._client.deploy_vault()

    def remove_vault(self) -> dict:
        return self._client.remove_vault()

    def get_vault_script(self) -> SetupOptions:
        return self._client.get_vault_script()

    def get_vault_status(self) -> ServiceDeploymentInformation:
        return self._client.get_vault_status()

    def deploy_minio(self) -> dict:
        return self._client.deploy_minio()

    def remove_minio(self) -> dict:
        return self._client.remove_minio()

    def get_minio_script(self) -> SetupOptions:
        return self._client.get_minio_script()

    def get_minio_status(self) -> ServiceDeploymentInformation:
        return self._client.get_minio_status()

    def deploy_database(self) -> dict:
        return self._client.deploy_database()

    def get_database_script(self) -> SetupOptions:
        return self._client.get_database_script()

    def get_database_status(self) -> ServiceDeploymentInformation:
        return self._client.get_database_status()

    def remove_database(self) -> dict:
        return self._client.remove_database()

    def deploy_rabbitmq(self) -> dict:
        return self._client.deploy_rabbitmq()

    def remove_rabbitmq(self) -> dict:
        return self._client.remove_rabbitmq()

    def get_rabbitmq_script(self) -> SetupOptions:
        return self._client.get_rabbitmq_script()

    def get_rabbitmq_status(self) -> ServiceDeploymentInformation:
        return self._client.get_rabbitmq_status()

    def deploy_redis(self) -> dict:
        return self._client.deploy_redis()

    def remove_redis(self) -> dict:
        return self._client.remove_redis()

    def get_redis_script(self) -> SetupOptions:
        return self._client.get_redis_script()

    def get_redis_status(self) -> ServiceDeploymentInformation:
        return self._client.get_redis_status()

    def deploy_supervisor(self) -> dict:
        return self._client.deploy_supervisor()

    def remove_supervisor(self) -> dict:
        return self._client.remove_supervisor()

    def get_supervisor_script(self) -> SetupOptions:
        return self._client.get_supervisor_script()

    def get_supervisor_status(self) -> ServiceDeploymentInformation:
        return self._client.get_supervisor_status()

    def deploy(self, module: ModuleCode, credentials=None, provider=None) -> dict:
        """
            Deploy a module
            :param module: Name of the module
        """
        return self._client.deploy(module, credentials, provider)

    def remove(self, module: ModuleCode, provider=None) -> dict:
        """
            Remove deployed module
            :param module: Name of the module
        """
        return self._client.remove(module, provider)

    def get_script(self, module: ModuleCode, credentials=None, provider=None) -> SetupOptions:
        """
            Get deployment script
            :param module: Name of the module
        """
        return self._client.get_script(module, credentials, provider)

    def get_status(self, module: ModuleCode) -> ServiceDeploymentInformation:
        """
            Get module status
            :param module: Name of the module
        """
        return self._client.get_status(module)

    def test_deployer(self) -> dict:
        """
            Test connection deployer
            :param module: Name of the module
        """
        return self._client.test_deployer()

    def execute_command_inside_container(self, image: str, command: str, environment: dict) -> CommandStatus:
        """
        Execute command inside container

        :param environment:
        :param image:
        :param command:
        :return:
        """
        return self._client.execute_command_inside_container(image, command, environment)
