from django.http import JsonResponse
from rest_framework.response import Response
from tesla_ce_supervisor.apps.api.serializers.task_log_serializer import TaskLogSerializer
from .base import BaseViewsets


class TaskViewSet(BaseViewsets):
    def retrieve(self, request, pk=None):
        module = pk.upper()

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
