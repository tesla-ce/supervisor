import json

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import action
from .base import BaseViewsets, BaseConfigViewsets


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


class ConfigViewSet(BaseConfigViewsets):
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

    @action(detail=False, methods=['post'])
    def create_database(self, request):
        db_name = request.data.get('db_name')
        db_user = request.data.get('db_user')
        db_password = request.data.get('db_password')
        self.client.create_database(db_name, db_user, db_password)

        return Response()

    @action(detail=False, methods=['get'])
    def all_config(self, request):
        result = self.client.tesla.get_config().get_config()
        return JsonResponse(result)
