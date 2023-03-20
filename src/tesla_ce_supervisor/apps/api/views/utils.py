from rest_framework.views import APIView
from rest_framework.response import Response
from tesla_ce_supervisor.lib.client import SupervisorClient


class Status(APIView):
    def get(self, request, format=None):
        return Response({'status': 'running'})


class VaultConfiguration(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        client = SupervisorClient()
        data = client.get_vault_configuration()
        return Response(data)
