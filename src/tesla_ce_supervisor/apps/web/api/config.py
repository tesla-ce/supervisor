import abc
import typing

from django.http import HttpResponse, JsonResponse
from rest_framework import status
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

    def get(self, request, step=None, format=None):
        data = {}
        if self.module == 'SUPERVISOR':
            data = {"config": self.client.tesla.get_config().get_config()}
        elif self.module == 'TESLA':
            data = {"step": step}

        response = self.client.make_request_to_supervisor_service('GET', '/supervisor/api/admin/config/{}/'.format(self.module), data)
        if response is not None:
            return JsonResponse(response.json())
        return JsonResponse({})


class APIConfigVault(BaseAPIDeploy):
    """
        Manage vault connection
    """
    module = 'VAULT'


class APIConfigDatabase(BaseAPIDeploy):
    """
        Manage database connection
    """
    module = 'DATABASE'


class APIConfigRabbitmq(BaseAPIDeploy):
    """
        Manage Rabbitmq connection
    """
    module = 'RABBITMQ'


class APIConfigRedis(BaseAPIDeploy):
    """
        Manage Redis connection
    """
    module = 'REDIS'


class APIConfigSupervisor(BaseAPIDeploy):
    """
        Manage Supervisor connection
    """
    module = 'SUPERVISOR'


class APIConfigMinIO(BaseAPIDeploy):
    """
        Manage MinIO connection
    """
    module = 'MINIO'


class APIConfigTeSLA(BaseAPIDeploy):
    """
        Manage ConfigTeSLA connection
    """
    module = 'TESLA'
