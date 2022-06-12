import typing

from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.lib.exceptions import TeslaException


class APICheckDNS(APIView):
    """
        Check DNS registration status for required domains
    """
    def get(self, request, format=None):
        client = SupervisorClient()
        json_resp = client.check_dns()
        return JsonResponse(json_resp)


class APICheckLoadBalancer(APIView):
    """
        Check Load Balancer status
    """
    def get(self, request, format=None):
        client = SupervisorClient()
        json_resp = client.check_lb()
        return JsonResponse(json_resp)

