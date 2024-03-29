"""supervisor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.views.generic.base import RedirectView
from tesla_ce_supervisor.lib.client import SupervisorClient

urlpatterns = [
    path('', include('django_prometheus.urls')),
    path('supervisor/api/', include('tesla_ce_supervisor.apps.api.urls')),
]

if settings.SETUP_MODE == 'SETUP' or settings.SETUP_MODE == 'DEV':
    urlpatterns += [
        path('setup/', include('tesla_ce_supervisor.apps.web.urls')),
        path('', RedirectView.as_view(pattern_name='setup_home', permanent=True)),
    ]
elif settings.SETUP_MODE == 'AUTO':
    client = SupervisorClient()
    client.auto_deploy()
