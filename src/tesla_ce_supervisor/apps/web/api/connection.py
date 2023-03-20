from django.http import JsonResponse
from .base import BaseAPISupervisor


class BaseAPIDeploy(BaseAPISupervisor):
    """
        Base class for deployment
    """
    def get(self, request, format=None):
        if self.module == 'SUPERVISOR':
            response = self.client.make_request_to_supervisor_service('GET', '/supervisor/api/admin/status/SUPERVISOR', {})
            if response is None:
                return JsonResponse({})
            json_resp = {
                'valid': False,
                'ready': False,
                'errors': None,
                'info': None
            }
            json_resp_aux = response.json()

            if 'status' in json_resp_aux and 'last_config' in json_resp_aux and 'version' in json_resp_aux:
                if json_resp_aux['status'] >= 2:
                    json_resp['valid'] = True

                if json_resp_aux['status'] >= 3:
                    json_resp['ready'] = True

                json_resp['info'] = "Last config: {}. Version: {}. Status: {}".format(json_resp_aux['last_config'],
                                                                                      json_resp_aux['version'],
                                                                                      json_resp_aux['status'])
        else:
            response = self.client.make_request_to_supervisor_service('GET', '/supervisor/api/admin/connection/{}/'.format(self.module), {})
            if response is None:
                return JsonResponse({})
            json_resp = response.json()
        return JsonResponse(json_resp)


class APIConnectionVault(BaseAPIDeploy):
    """
        Manage vault connection
    """
    module = 'VAULT'


class APIConnectionDatabase(BaseAPIDeploy):
    """
        Manage database connection
    """
    module = 'DATABASE'


class APIConnectionRabbitmq(BaseAPIDeploy):
    """
        Manage Rabbitmq connection
    """
    module = 'RABBITMQ'


class APIConnectionRedis(BaseAPIDeploy):
    """
        Manage Redis connection
    """
    module = 'REDIS'


class APIConnectionSupervisor(BaseAPIDeploy):
    """
        Manage Supervisor connection
    """
    module = 'SUPERVISOR'

class APIConnectionMinIO(BaseAPIDeploy):
    """
        Manage MinIO connection
    """
    module = 'MINIO'
