from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from tesla_ce_supervisor.lib.client import SupervisorClient


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
        status = client.check_lb()
        return JsonResponse(status.to_json())


class APICheckDatabase(APIView):
    """
        Check Database status
    """
    def get(self, request, format=None):
        client = SupervisorClient()
        status = client.check_database()
        return JsonResponse(status.to_json())


class APICheckMinio(APIView):
    """
        Check MinIO status
    """
    def get(self, request, format=None):
        client = SupervisorClient()
        status = client.check_minio()
        return JsonResponse(status.to_json())


class APICheckRabbitMQ(APIView):
    """
        Check MinIO status
    """
    def get(self, request, format=None):
        client = SupervisorClient()
        status = client.check_rabbitmq()
        return JsonResponse(status.to_json())


class APICheckRedis(APIView):
    """
        Check Redis status
    """
    def get(self, request, format=None):
        client = SupervisorClient()
        status = client.check_redis()
        return JsonResponse(status.to_json())


class APICheckVault(APIView):
    """
        Check Vault status
    """
    def get(self, request, format=None):
        client = SupervisorClient()
        status = client.check_vault()
        return JsonResponse(status.to_json())


class APICheckSupervisor(APIView):
    """
        Check TeSLA CE Supervisor status
    """
    def get(self, request, format=None):
        client = SupervisorClient()
        status = client.check_supervisor()
        return JsonResponse(status.to_json())
