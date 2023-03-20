import abc
import typing

from django.http import JsonResponse
from rest_framework.views import APIView
from tesla_ce_supervisor.lib.deploy.base import ModuleCode
from tesla_ce_supervisor.lib.client import SupervisorClient


class BaseAPISupervisor(APIView, abc.ABC):
    """
        Base class for deployment
    """
    module: typing.Optional[ModuleCode] = None
    _client = None

    @property
    def client(self):
        if self._client is None:
            self._client = SupervisorClient.get_instance()

        return self._client
