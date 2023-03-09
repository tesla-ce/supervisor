from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.setup.home_view,  name='setup_home'),
    path('environment', views.setup.env_view,  name='setup_environment'),
    path('tesla_info', views.setup.tesla_basic_info,  name='setup_tesla_basic_info'),
    path('load_balancer', views.setup.lb_view,  name='setup_load_balancer'),
    path('supervisor', views.setup.supervisor_view,  name='setup_supervisor'),
    path('services/config', views.setup.services.service_configuration,  name='setup_services_config'),
    path('services/deploy', views.setup.services.service_deployment,  name='setup_services_deploy'),
    path('services/register', views.setup.services.service_deployment,  name='setup_services_register'),
    path('tesla', views.setup.configure_tesla.configure_tesla_view,  name='setup_tesla_configure'),
    path('tesladeploycore', views.setup.deploy_tesla_core.deploy_tesla_core_view,  name='setup_tesla_deploy_core'),
    path('tesladeployworkers', views.setup.deploy_tesla_workers.deploy_tesla_workers_view,
         name='setup_tesla_deploy_workers'),
    path('tesladeployinstruments', views.setup.deploy_tesla_instruments.deploy_tesla_instruments_view,
         name='setup_tesla_deploy_instruments'),
    path('teslaconfiguremoodle', views.setup.configure_tesla_moodle_view, name='setup_tesla_config_moodle'),
    path('tesladeploymoodle', views.setup.deploy_tesla_moodle.deploy_tesla_moodle_view,
         name='setup_tesla_deploy_moodle'),
    
    path('step1', views.setup.steps.step1,  name='setup_step1'),
    path('step2', views.setup.steps.step2,  name='setup_step2'),
    path('step3', views.setup.steps.step3,  name='setup_step3'),

    path('api/', include('tesla_ce_supervisor.apps.web.api.urls'))
]
