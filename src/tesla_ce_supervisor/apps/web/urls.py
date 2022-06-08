from django.urls import path

from . import views

urlpatterns = [
    path('', views.setup.step1,  name='setup_step1'),
    path('step2', views.setup.step2,  name='setup_step2'),
    path('step3', views.setup.step3,  name='setup_step3'),

    path('api/vault_config', views.VaultConfigurationAPIView.as_view(), name='setup_api_vault_config')
]
