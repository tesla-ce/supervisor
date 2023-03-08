import abc
import base64
import typing
import json

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
    _client = None

    @property
    def client(self):
        if self._client is None:
            self._client = SupervisorClient.get_instance()

        return self._client

    def get_credentials(self):
        credentials = None
        if self.module.lower() in ['api', 'beat', 'worker-all', 'worker-enrolment', 'worker-enrolment-storage',
                                   'worker-enrolment-validation', 'worker-verification', 'worker-alerts',
                                   'worker-reporting', 'lapi']:
            data = {"module": self.module.lower()}
            response = self.client.make_request_to_supervisor_service('POST', '/supervisor/api/admin/config/role_secret/', data)
            credentials = json.loads(response.json())

        if self.module.lower() in ['tfr', 'tpt', 'tks']:
            credentials = self.client.register_provider(self.module.lower())



        return credentials

    def get(self, request, format=None):
        credentials = self.get_credentials()

        response = self.client.get_deployer().get_script(self.module, credentials)
        json_resp = response.to_json()
        if 'zip' in request.query_params and request.query_params['zip'] == '1':
            json_resp['zip'] = 'data:application/zip;base64,{}'.format(base64.b64encode(response.get_zip()).decode())
        return JsonResponse(json_resp)

    def post(self, request, format=None):
        try:
            credentials = self.get_credentials()

            response = self.client.deploy.deploy(self.module, credentials)
            self.client.tesla.persist_configuration()

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


class APIDeployAPI(BaseAPIDeploy):
    """
        Manage TeSLA CE API deployment
    """
    module = 'API'


class APIDeployBeat(BaseAPIDeploy):
    """
        Manage TeSLA CE Beat deployment
    """
    module = 'BEAT'


class APIDeployAPIWorkerAll(BaseAPIDeploy):
    """
        Manage TeSLA CE API worker all deployment
    """
    module = 'WORKER-ALL'


class APIDeployAPIWorkerEnrolment(BaseAPIDeploy):
    """
        Manage TeSLA CE API worker enrolment deployment
    """
    module = 'WORKER-ENROLMENT'


class APIDeployAPIWorkerEnrolmentStorage(BaseAPIDeploy):
    """
        Manage TeSLA CE API worker enrolment storage deployment
    """
    module = 'WORKER-ENROLMENT-STORAGE'


class APIDeployAPIWorkerEnrolmentValidation(BaseAPIDeploy):
    """
        Manage TeSLA CE API worker enrolment validation deployment
    """
    module = 'WORKER-ENROLMENT-VALIDATION'


class APIDeployAPIWorkerVerification(BaseAPIDeploy):
    """
        Manage TeSLA CE API worker verification deployment
    """
    module = 'WORKER-VERIFICATION'


class APIDeployAPIWorkerAlerts(BaseAPIDeploy):
    """
        Manage TeSLA CE API worker alerts deployment
    """
    module = 'WORKER-ALERTS'


class APIDeployAPIWorkerReporting(BaseAPIDeploy):
    """
        Manage TeSLA CE API worker reporting deployment
    """
    module = 'WORKER-REPORTING'


class APIDeployLAPI(BaseAPIDeploy):
    """
        Manage TeSLA CE LAPI deployment
    """
    module = 'LAPI'


class APIDeployDashboard(BaseAPIDeploy):
    """
        Manage TeSLA CE Dasboard deployment
    """
    module = 'DASHBOARD'


class APIDeployMoodle(BaseAPIDeploy):
    """
        Manage TeSLA CE Moodle deployment
    """
    module = 'MOODLE'


class APIDeployFR(BaseAPIDeploy):
    """
        Manage TeSLA CE Face Recognition deployment
    """
    module = 'TFR'


class APIDeployKS(BaseAPIDeploy):
    """
        Manage TeSLA CE Keystroke deployment
    """
    module = 'TKS'


class APIDeployTPT(BaseAPIDeploy):
    """
        Manage TeSLA CE TPT deployment
    """
    module = 'TPT'
