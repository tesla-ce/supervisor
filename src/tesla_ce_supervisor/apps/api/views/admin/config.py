import json

from django.shortcuts import render
from django.http import Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from tesla_ce_supervisor.lib.client import SupervisorClient
from rest_framework import viewsets

# Create your views here.


class BaseViewsets(viewsets.ViewSet):
    _client = None

    @property
    def client(self):
        if self._client is None:
            self._client = SupervisorClient.get_instance()

        return self._client


class StatusViewSet(BaseViewsets):
    def retrieve(self, request, pk=None):
        # status = self.client.catalog.check_status(pk)
        if pk == 'SUPERVISOR':
            status = self.client.supervisor_status()
            return Response(status)


class ConnectionViewSet(BaseViewsets):
    def retrieve(self, request, pk=None):
        resp = self.client.catalog.check_connection(pk)
        content = resp.to_json()

        return Response(content)


class ConfigViewSet(BaseViewsets):
    def retrieve(self, request, pk=None):
        module = pk.upper()
        result = self.client.configure_service(module, request)

        return JsonResponse(result)

    def list(self, request):
        token = request.GET.get('token')

        if self.client.check_api_signed_token(token=token) is False:
            return JsonResponse(status=403, data={})

        result = self.client.tesla.get_config().get_config()

        return JsonResponse(result)

    def create(self, request):
        token = request.GET.get('token')
        if self.client.check_api_signed_token(token=token) is False:
            return JsonResponse(status=403, data={})

        self.client.task.create_from_core(command=request.data.get('command'),
                                          status=request.data.get('status'))

        return JsonResponse({})

    @action(detail=False, methods=['post'])
    def role_secret(self, request):
        module = request.data.get('module').lower()
        credentials = self.client.tesla.get_module_credentials(module)
        return Response(json.dumps(credentials))
