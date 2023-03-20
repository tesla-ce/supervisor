from django.http import JsonResponse
from rest_framework.views import APIView
from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.lib.exceptions import TeslaException


class APIVaultInitKV(APIView):
    """
        Vault KV engine manipulation
    """
    def get(self, request, format=None):
        client = SupervisorClient()
        json_resp = {}
        return JsonResponse(json_resp)

    def post(self, request, format=None):
        try:
            response = self.deploy()
        except TeslaException as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        return JsonResponse(response)

    def delete(self, request, format=None):
        try:
            response = self.remove()
        except TeslaException as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        return JsonResponse(response)

