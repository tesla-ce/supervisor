from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from tesla_ce_supervisor.lib.tesla import TeslaClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status
from tesla_ce_supervisor.apps.web.forms.base import ConfigForm
from tesla_ce_supervisor.apps.web.forms.environment import NomadConsulForm, SwarmForm
from tesla_ce_supervisor.apps.web.forms.tesla_basics import TeslaBasicInfoForm

def service_deployment(request):
    client = TeslaClient()
    client.get_config_path()
    client.load_configuration()

    options_env = None
    if client.get("DEPLOYMENT_CATALOG_SYSTEM") == 'consul' and client.get("DEPLOYMENT_ORCHESTRATOR") == 'nomad':
        options_env = 'nomad_consul'
    elif client.get("DEPLOYMENT_CATALOG_SYSTEM") == 'swarm' and client.get("DEPLOYMENT_ORCHESTRATOR") == 'swarm':
        options_env = 'swarm'
    if client.get("DEPLOYMENT_SERVICES"):
        options_mode = 'development'
    else:
        options_mode = 'production'

    context = {
        'options': {
            'environment': options_env,
            'mode': options_mode,
            'catalog': client.get("DEPLOYMENT_CATALOG_SYSTEM"),
        },
    }

    if request.method == 'POST':
        return JsonResponse({'errors': {}})
    return render(request, 'services/deploy_services.html', context)
