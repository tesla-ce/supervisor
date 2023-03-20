from django.http import JsonResponse
from .base import BaseAPISupervisor


class BaseAPITask(BaseAPISupervisor):
    """
        Base class for deployment
    """
    def get(self, request, format=None):
        task_id = request.query_params.get('task_id')
        response = self.client.make_request_to_supervisor_service('GET', '/supervisor/api/admin/task/?task_id={}'.format(task_id), {})

        if response is not None:
            return JsonResponse(response.json(), safe=False)

        return JsonResponse({})


class APILogConfig(BaseAPITask):
    """
        Manage vault connection
    """
    module = 'LOG'
