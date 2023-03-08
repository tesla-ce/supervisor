import abc
import base64
import typing

from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from tesla_ce_supervisor.lib.deploy.base import ModuleCode
from tesla_ce_supervisor.lib.client import SupervisorClient


class BaseAPIDeploy(APIView, abc.ABC):
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

    def get(self, request):
        json_resp = self.client.check_module(self.module)
        return JsonResponse(json_resp)


class APICheckDNS(BaseAPIDeploy):
    """
        Check DNS registration status for required domains
    """
    module = 'DNS'


class APICheckLoadBalancer(BaseAPIDeploy):
    """
        Check Load Balancer status
    """
    module = 'LB'


class APICheckDatabase(BaseAPIDeploy):
    """
        Check Database status
    """
    module = 'DATABASE'


class APICheckMinio(BaseAPIDeploy):
    """
        Check MinIO status
    """
    module = 'MINIO'


class APICheckRabbitMQ(BaseAPIDeploy):
    """
        Check MinIO status
    """
    module = 'RABBITMQ'


class APICheckRedis(BaseAPIDeploy):
    """
        Check Redis status
    """
    module = 'REDIS'


class APICheckVault(BaseAPIDeploy):
    """
        Check Vault status
    """
    module = 'VAULT'


class APICheckSupervisor(BaseAPIDeploy):
    """
        Check TeSLA CE Supervisor status
    """
    module = 'SUPERVISOR'


class APICheckAPI(BaseAPIDeploy):
    """
        Check TeSLA CE Supervisor status
    """
    module = 'API'


class APICheckBeat(BaseAPIDeploy):
    """
        Check TeSLA CE Supervisor status
    """
    module = 'BEAT'


class APICheckAPIWorkerAll(BaseAPIDeploy):
    """
        Manage TeSLA CE API worker all deployment
    """
    module = 'WORKER-ALL'


class APICheckAPIWorkerEnrolment(BaseAPIDeploy):
    """
        Manage TeSLA CE API worker enrolment deployment
    """
    module = 'WORKER-ENROLMENT'


class APICheckAPIWorkerEnrolmentStorage(BaseAPIDeploy):
    """
        Manage TeSLA CE API worker enrolment storage deployment
    """
    module = 'WORKER-ENROLMENT-STORAGE'


class APICheckAPIWorkerEnrolmentValidation(BaseAPIDeploy):
    """
        Manage TeSLA CE API worker enrolment validation deployment
    """
    module = 'WORKER-ENROLMENT-VALIDATION'


class APICheckAPIWorkerVerification(BaseAPIDeploy):
    """
        Manage TeSLA CE API worker verification deployment
    """
    module = 'WORKER-VERIFICATION'


class APICheckAPIWorkerAlerts(BaseAPIDeploy):
    """
        Manage TeSLA CE API worker alerts deployment
    """
    module = 'WORKER-ALERTS'


class APICheckAPIWorkerReporting(BaseAPIDeploy):
    """
        Manage TeSLA CE API worker reporting deployment
    """
    module = 'WORKER-REPORTING'

class APICheckLAPI(BaseAPIDeploy):
    """
        Check TeSLA CE LAPI deployment
    """
    module = 'LAPI'


class APICheckDashboard(BaseAPIDeploy):
    """
        Check TeSLA CE Dasboard deployment
    """
    module = 'DASHBOARD'


class APICheckMoodle(BaseAPIDeploy):
    """
        Check TeSLA CE Moodle deployment
    """
    module = 'MOODLE'


class APICheckFR(BaseAPIDeploy):
    """
        Check TeSLA CE Face Recognition deployment
    """
    module = 'TFR'


class APICheckKS(BaseAPIDeploy):
    """
        Check TeSLA CE Keystroke deployment
    """
    module = 'TKS'


class APICheckTPT(BaseAPIDeploy):
    """
        Check TeSLA CE TPT deployment
    """
    module = 'TPT'

