from django.http import JsonResponse
from django.shortcuts import render

from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status
from tesla_ce_supervisor.apps.web.forms.base import ConfigForm
from tesla_ce_supervisor.apps.web.forms.environment import NomadConsulForm, SwarmForm


def environment(request):
    client = SupervisorClient()

    options_env = None
    if client.tesla.get("DEPLOYMENT_CATALOG_SYSTEM") == 'consul' and client.tesla.get("DEPLOYMENT_ORCHESTRATOR") == 'nomad':
        options_env = 'nomad_consul'
    elif client.tesla.get("DEPLOYMENT_CATALOG_SYSTEM") == 'swarm' and client.tesla.get("DEPLOYMENT_ORCHESTRATOR") == 'swarm':
        options_env = 'swarm'
    if client.tesla.get("DEPLOYMENT_SERVICES"):
        options_mode = 'development'
    else:
        options_mode = 'production'
    form: ConfigForm = None
    if options_env == 'nomad_consul':
        form = NomadConsulForm()
    elif options_env == 'swarm':
        form = SwarmForm()
    form.load_config(client.tesla.get_config())
    context = {
        'options': {
            'environment': options_env,
            'mode': options_mode,
            'setup_status': client.tesla.get("DEPLOYMENT_STATUS"),
        },
        'form': form,
    }
    if request.method == 'POST':
        if options_env == 'nomad_consul':
            form = NomadConsulForm(request.POST)
        elif options_env == 'swarm':
            form = SwarmForm(request.POST)
        if form.is_valid():
            form.update_config(client.tesla.get_config())
            client.tesla.get_config().set('DEPLOYMENT_STATUS', 2)
            client.tesla.persist_configuration()
            return JsonResponse({'redirect_url': get_url_from_status(client)})
        return JsonResponse({'errors': form.errors})
    return render(request, 'environment.html', context)
