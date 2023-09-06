from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status
from tesla_ce_supervisor.apps.web.forms.base import ConfigForm
from tesla_ce_supervisor.apps.web.forms.environment import NomadConsulForm, SwarmForm
from tesla_ce_supervisor.apps.web.forms.service_database import TeslaServiceDatabaseForm
from tesla_ce_supervisor.apps.web.forms.service_redis import TeslaServiceRedisForm
from tesla_ce_supervisor.apps.web.forms.service_minio import TeslaServiceMinioForm
from tesla_ce_supervisor.apps.web.forms.service_rabbitmq import TeslaServiceRabbitMqForm
from tesla_ce_supervisor.apps.web.forms.service_vault import TeslaServiceVaultForm

def service_configuration(request):
    client = SupervisorClient.get_instance()

    form_db = TeslaServiceDatabaseForm()
    form_redis = TeslaServiceRedisForm()
    form_minio = TeslaServiceMinioForm()
    form_rabbitmq = TeslaServiceRabbitMqForm()
    form_vault = TeslaServiceVaultForm()

    forms = [form_db, form_redis, form_minio, form_rabbitmq, form_vault]
    for form in forms:
        form.load_config(client.tesla.get_config())

    context = {
        'options': {
            'setup_status': client.tesla.get("DEPLOYMENT_STATUS"),
        },
        'form_db': form_db,
        'form_redis': form_redis,
        'form_minio': form_minio,
        'form_rabbitmq': form_rabbitmq,
        'form_vault': form_vault,
    }

    if request.method == 'POST':
        form_db = TeslaServiceDatabaseForm(request.POST)
        form_redis = TeslaServiceRedisForm(request.POST)
        form_minio = TeslaServiceMinioForm(request.POST)
        form_rabbitmq = TeslaServiceRabbitMqForm(request.POST)
        form_vault = TeslaServiceVaultForm(request.POST)

        forms = [form_db, form_redis, form_minio, form_rabbitmq, form_vault]

        for form in forms:
            if form.is_valid():
                form.update_config(client.tesla.get_config())
                client.tesla.persist_configuration()
            else:
                return JsonResponse({'errors': form.errors})

        client.tesla.get_config().set('DEPLOYMENT_STATUS', 7)
        client.tesla.persist_configuration()
        return JsonResponse({'redirect_url': get_url_from_status(client)})
        # return JsonResponse({'errors': {}})
    return render(request, 'services/config_services.html', context)
