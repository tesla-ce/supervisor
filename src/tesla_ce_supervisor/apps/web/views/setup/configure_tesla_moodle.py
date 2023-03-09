from django.http import JsonResponse
from django.shortcuts import render

from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status
from tesla_ce_supervisor.apps.web.forms.tesla_moodle import TeslaMoodleForm


def configure_tesla_moodle_view(request):
    client = SupervisorClient.get_instance()

    form = TeslaMoodleForm()
    form.load_config(client.tesla.get_config())

    options_env = None
    if client.tesla.get("DEPLOYMENT_CATALOG_SYSTEM") == 'consul' and client.tesla.get("DEPLOYMENT_ORCHESTRATOR") == 'nomad':
        options_env = 'nomad_consul'
    elif client.tesla.get("DEPLOYMENT_CATALOG_SYSTEM") == 'swarm' and client.tesla.get("DEPLOYMENT_ORCHESTRATOR") == 'swarm':
        options_env = 'swarm'
    if client.tesla.get("DEPLOYMENT_SERVICES"):
        options_mode = 'development'
    else:
        options_mode = 'production'

    context = {
        'options': {
            'environment': options_env,
            'mode': options_mode,
            'catalog': client.tesla.get("DEPLOYMENT_CATALOG_SYSTEM"),
            'load_balancer': client.tesla.get("DEPLOYMENT_LB"),
            'base_domain': client.tesla.get("TESLA_DOMAIN"),
            'data_path': client.tesla.get("DEPLOYMENT_DATA_PATH"),
            'steps': ['configure_vault', 'db_migration', 'create_superuser', 'collect_statics', 'fixtures']
        },
        'form': form,
    }

    # client.tesla.persist_configuration()

    if request.method == 'POST':
        form = TeslaMoodleForm(request.POST)
        if form.is_valid():
            form.update_config(client.tesla.get_config())
            client.tesla.get_config().set('DEPLOYMENT_STATUS', 13)
            client.tesla.persist_configuration()

            return JsonResponse({'redirect_url': get_url_from_status(client)})
        return JsonResponse({'errors': form.errors})

    return render(request, 'tesla_config_moodle.html', context)
