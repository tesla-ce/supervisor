from .base import BaseDeploy
from ..setup_options import SetupOptions


class SwarmDeploy(BaseDeploy):

    def write_scripts(self) -> None:
        """
            Write deployment scripts
        """
        pass

    def deploy_lb(self) -> dict:
        """
            Deploy Load Balancer
        """
        return {}

    def get_lb_script(self) -> SetupOptions:
        """
            Get the script to deploy Load Balancer
        """
        script = SetupOptions()
        return script

    def deploy_vault(self) -> dict:
        """
            Deploy Hashicorp Vault
        """
        return {}

    def get_vault_script(self) -> SetupOptions:
        """
            Get the script to deploy Hashicorp Vault
        """
        script = SetupOptions()
        return script

    def deploy_minio(self) -> dict:
        """
            Deploy MinIO
        """
        return {}

    def get_minio_script(self) -> SetupOptions:
        """
            Get the script to deploy MinIO
        """
        script = SetupOptions()
        return script

    def deploy_redis(self) -> dict:
        """
            Deploy Redis
        """
        return {}

    def get_redis_script(self) -> SetupOptions:
        """
            Get the script to deploy Redis
        """
        script = SetupOptions()
        return script

    def deploy_database(self) -> dict:
        """
            Deploy Database
        """
        return {}

    def get_database_script(self) -> SetupOptions:
        """
            Get the script to deploy Database
        """
        script = SetupOptions()
        return script

    def deploy_rabbit(self) -> dict:
        """
            Deploy RabbitMQ
        """
        return {}

    def get_rabbit_script(self) -> SetupOptions:
        """
            Get the script to deploy RabbitMQ
        """
        script = SetupOptions()
        return script
