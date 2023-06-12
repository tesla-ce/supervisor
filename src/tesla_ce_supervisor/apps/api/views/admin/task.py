from django.http import JsonResponse
from rest_framework.response import Response
from tesla_ce_supervisor.apps.api.serializers.task_log_serializer import TaskLogSerializer
from .base import BaseViewsets


class TaskViewSet(BaseViewsets):
    def retrieve(self, request, pk=None):
        step = pk

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
            task = self.client.task.get_last_by_code(code=pk)
            result = {}
            if task:
                result = task.to_json()

            return JsonResponse(result)

    def list(self, request):
        task_id = request.query_params.get('task_id')
        queryset = self.client.task.get_lasts_tasks(task_id)

        serializer = TaskLogSerializer(queryset, many=True)
        return Response(serializer.data)
