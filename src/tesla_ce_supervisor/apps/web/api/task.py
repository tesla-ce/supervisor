import typing
import json

from django.http import JsonResponse
from tesla_ce_supervisor.lib.deploy.base import ModuleCode
from tesla_ce_supervisor.lib.client import SupervisorClient
from .base import BaseAPISupervisor


class BaseAPITask(BaseAPISupervisor):
    """
        Base class for deployment
    """
    module: typing.Optional[ModuleCode] = None

    @property
    def client(self):
        return SupervisorClient()

    def get(self, request, step, format=None):

        if step in ['vault_unseal', 'vault_init_kv', 'vault_init_transit', 'vault_init_roles', 'vault_init_policies']:
            status = self.client.tesla.check_vault_status()
            return_data = {
                'code': None,
                'status': None,
                'error_json': None,
                'type': None,
                'parent_task_id': None,
                'previous_task_id': None,
            }

            return_data['code'] = step
            if step == 'vault_unseal' and status['unsealed'] is True:
                return_data['status'] = 3

            elif step == 'vault_init_kv' and status['kv']['installed'] is True and status['kv']['read'] is True:
                return_data['status'] = 3

            elif step == 'vault_init_transit' and status['transit']['installed'] is True \
                    and status['transit']['read'] is True and status['transit']['sign'] is True:
                return_data['status'] = 3
            elif step == 'vault_init_roles' and status['approle']['installed'] is True \
                    and status['approle']['read'] is True:
                return_data['status'] = 3
            elif step == 'vault_init_policies' and status['policies']['read'] is True \
                    and status['policies']['is_valid'] is True:
                return_data['status'] = 3



            return JsonResponse(return_data)
        else:
            response = self.client.make_request_to_supervisor_service('GET', '/supervisor/api/admin/task/{}/'.format(step), {})

        if response is not None:
            return JsonResponse(response.json())
        return JsonResponse({})


class APITaskConfig(BaseAPITask):
    """
        Manage vault connection
    """
    module = 'CONFIG'
