from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.setup.home,  name='setup_home'),
    path('environment', views.setup.environment,  name='setup_environment'),
    path('step1', views.setup.step1,  name='setup_step1'),
    path('step2', views.setup.step2,  name='setup_step2'),
    path('step3', views.setup.step3,  name='setup_step3'),

    path('api/', include('tesla_ce_supervisor.apps.web.api.urls'))
]
