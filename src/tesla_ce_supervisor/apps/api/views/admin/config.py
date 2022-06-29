from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from tesla_ce_supervisor.lib.client import SupervisorClient
# Create your views here.


class Status(APIView):
    def get(self, request, format=None):
        return Response({'status': 'running'})
