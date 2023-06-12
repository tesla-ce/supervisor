import base64
from django.http import JsonResponse
from .base import BaseAPISupervisor


class BaseAPIDeploy(BaseAPISupervisor):
    """
        Base class for deployment
    """
    def post(self, request, step=None, format=None):
        data = {}
        if self.module == 'SUPERVISOR':
            data = {"config": self.client.tesla.get_config().get_config()}
        elif self.module == 'TESLA':
            data = {"step": step}

        response = self.client.make_request_to_supervisor_service('GET', '/supervisor/api/admin/config/{}/'.format(self.module), data)

        if self.module == 'SUPERVISOR':
            # todo: reboot supervisor service
            self.client.get_deployer().reboot_module('supervisor', wait_ready=True)

        if response is not None:
            return JsonResponse(response.json())
        return JsonResponse({})

    def get(self, request, step=None, format=None):
        #credentials = self.get_credentials()
        #[provider, instrument_id] = self.get_provider()

        response = self.client.get_deployer().get_script(step, tesla=self.client.tesla)

        json_resp = response.to_json()
        if 'zip' in request.query_params and request.query_params['zip'] == '1':
            json_resp['zip'] = 'data:application/zip;base64,{}'.format(base64.b64encode(response.get_zip()).decode())
        return JsonResponse(json_resp)


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
