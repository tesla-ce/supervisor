from django.shortcuts import render
from django.http import Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from tesla_ce_supervisor.lib.client import SupervisorClient
from rest_framework import viewsets

from tesla_ce_supervisor.apps.api.serializers.task_log_serializer import TaskLogSerializer


class BaseViewsets(viewsets.ViewSet):
    _client = None

    @property
    def client(self):
        if self._client is None:
            self._client = SupervisorClient.get_instance()

        return self._client


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
