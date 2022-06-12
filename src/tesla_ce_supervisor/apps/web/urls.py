from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.setup.home_view,  name='setup_home'),
    path('environment', views.setup.env_view,  name='setup_environment'),
    path('tesla_info', views.setup.tesla_basic_info,  name='setup_tesla_basic_info'),
    path('services/deploy', views.setup.services.service_deployment,  name='setup_services_deploy'),
    path('services/config', views.setup.services.service_configuration,  name='setup_services_config'),
    path('services/status', views.setup.services.service_status,  name='setup_services_status'),

    path('step1', views.setup.steps.step1,  name='setup_step1'),
    path('step2', views.setup.steps.step2,  name='setup_step2'),
    path('step3', views.setup.steps.step3,  name='setup_step3'),

    path('api/', include('tesla_ce_supervisor.apps.web.api.urls'))
]
