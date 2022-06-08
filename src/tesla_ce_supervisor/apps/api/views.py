from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tesla_ce_supervisor.lib.client import SupervisorClient
# Create your views here.


class VaultConfiguration(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        client = SupervisorClient()
        data = client.get_vault_configuration()
        return Response(data)
