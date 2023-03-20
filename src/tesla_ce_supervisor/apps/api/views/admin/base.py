from rest_framework import viewsets
from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.apps.api.permissions import AdminPermission, ConfigPermission


class BaseViewsets(viewsets.ViewSet):
    _client = None
    permission_classes = [AdminPermission]

    @property
    def client(self):
        if self._client is None:
            self._client = SupervisorClient.get_instance()

        return self._client


class BaseConfigViewsets(BaseViewsets):
    permission_classes = [ConfigPermission]
