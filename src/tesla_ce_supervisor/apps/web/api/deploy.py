import abc
import base64
import typing

from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from tesla_ce_supervisor.lib.deploy.base import ModuleCode
from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.lib.exceptions import TeslaException


class BaseAPIDeploy(APIView, abc.ABC):
    """
        Base class for deployment
    """
    module: typing.Optional[ModuleCode] = None

    @property
    def client(self):
        return SupervisorClient()

    def get(self, request, format=None):
        response = self.client.get_deployer().get_script(self.module)
        json_resp = response.to_json()
        if 'zip' in request.query_params and request.query_params['zip'] == '1':
            json_resp['zip'] = 'data:application/zip;base64,{}'.format(base64.b64encode(response.get_zip()).decode())
        return JsonResponse(json_resp)

    def post(self, request, format=None):
        try:
            response = self.client.get_deployer().deploy(self.module)
        except TeslaException as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        return JsonResponse(response)

    def delete(self, request, format=None):
        try:
            response = self.client.get_deployer().remove(self.module)
        except TeslaException as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        return JsonResponse(response)


class APIDeployLoadBalancer(BaseAPIDeploy):
    """
        Manage Load Balancer deployment
    """
    module = 'LB'


class APIDeployVault(BaseAPIDeploy):
    """
        Manage Vault deployment
    """
    module = 'VAULT'


class APIDeployDatabase(BaseAPIDeploy):
    """
        Manage Database deployment
    """
    module = 'DATABASE'


class APIDeployMinio(BaseAPIDeploy):
    """
        Manage MinIO deployment
    """
    module = 'MINIO'


class APIDeployRedis(BaseAPIDeploy):
    """
        Manage Redis deployment
    """
    module = 'REDIS'


class APIDeployRabbitMQ(BaseAPIDeploy):
    """
        Manage RabbitMQ deployment
    """
    module = 'RABBITMQ'


class APIDeploySupervisor(BaseAPIDeploy):
    """
        Manage TeSLA CE Supervisor deployment
    """
    module = 'SUPERVISOR'
