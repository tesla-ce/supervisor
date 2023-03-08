import abc
import typing

from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from tesla_ce_supervisor.lib.deploy.base import ModuleCode
from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.lib.exceptions import TeslaException


class BaseAPITask(APIView, abc.ABC):
    """
        Base class for deployment
    """
    module: typing.Optional[ModuleCode] = None

    @property
    def client(self):
        return SupervisorClient()

    def get(self, request, step, format=None):
        response = self.client.make_request_to_supervisor_service('GET', '/supervisor/api/admin/task/{}/'.format(step), {})

        if response is not None:
            return JsonResponse(response.json())
        return JsonResponse({})


class APITaskConfig(BaseAPITask):
    """
        Manage vault connection
    """
    module = 'CONFIG'
