import abc
import base64
import typing

from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.lib.exceptions import TeslaException


class BaseAPIDeploy(APIView, abc.ABC):
    """
        Base class for deployment
    """
    script: typing.Callable = None
    deploy: typing.Callable = None
    remove: typing.Callable = None
    client: SupervisorClient = None

    def get(self, request, format=None):
        self.client._tesla.get_config_path()
        self.client._tesla.load_configuration()

        response = self.script()
        json_resp = response.to_json()
        if 'zip' in request.query_params and request.query_params['zip'] == '1':
            json_resp['zip'] = 'data:application/zip;base64,{}'.format(base64.b64encode(response.get_zip()).decode())
        return JsonResponse(json_resp)

    def post(self, request, format=None):
        try:
            self.client._tesla.get_config_path()
            self.client._tesla.load_configuration()
            response = self.deploy()
        except TeslaException as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        return JsonResponse(response)

    def delete(self, request, format=None):
        try:
            self.client._tesla.get_config_path()
            self.client._tesla.load_configuration()
            response = self.remove()
        except TeslaException as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        return JsonResponse(response)


class APIDeployLoadBalancer(BaseAPIDeploy):
    """
        Manage Load Balancer deployment
    """
    client = SupervisorClient()
    script = client.get_deployer().get_lb_script
    deploy = client.get_deployer().deploy_lb
    remove = client.get_deployer().remove_lb


class APIDeployVault(BaseAPIDeploy):
    """
        Manage Vault deployment
    """
    client = SupervisorClient()
    script = client.get_deployer().get_vault_script
    deploy = client.get_deployer().deploy_vault
    remove = client.get_deployer().remove_vault


class APIDeployDatabase(BaseAPIDeploy):
    """
        Manage Database deployment
    """
    client = SupervisorClient()
    script = client.get_deployer().get_database_script
    deploy = client.get_deployer().deploy_database
    remove = client.get_deployer().remove_database


class APIDeployMinio(BaseAPIDeploy):
    """
        Manage MinIO deployment
    """
    client = SupervisorClient()
    script = client.get_deployer().get_minio_script
    deploy = client.get_deployer().deploy_minio
    remove = client.get_deployer().remove_minio


class APIDeployRedis(BaseAPIDeploy):
    """
        Manage Redis deployment
    """
    client = SupervisorClient()
    script = client.get_deployer().get_redis_script
    deploy = client.get_deployer().deploy_redis
    remove = client.get_deployer().remove_redis


class APIDeployRabbitMQ(BaseAPIDeploy):
    """
        Manage RabbitMQ deployment
    """
    client = SupervisorClient()
    script = client.get_deployer().get_rabbitmq_script
    deploy = client.get_deployer().deploy_rabbitmq
    remove = client.get_deployer().remove_rabbitmq


class APIDeploySupervisor(BaseAPIDeploy):
    """
        Manage TeSLA CE Supervisor deployment
    """
    client = SupervisorClient()
    script = client.get_deployer().get_supervisor_script
    deploy = client.get_deployer().deploy_supervisor
    remove = client.get_deployer().remove_supervisor
