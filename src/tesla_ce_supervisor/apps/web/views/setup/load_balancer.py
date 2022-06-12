from django.http import JsonResponse
from django.shortcuts import render

from tesla_ce_supervisor.lib.tesla import TeslaClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status


def lb_view(request):
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

    # Set Traefik as the load balancer for this deployment
    client.get_config().set("DEPLOYMENT_LB", 'traefik')
    client.persist_configuration()

    context = {
        'options': {
            'environment': options_env,
            'mode': options_mode,
            'load_balancer': client.get("DEPLOYMENT_LB"),
            'base_domain': client.get("TESLA_DOMAIN"),
        }
    }
    if request.method == 'POST':
        # TODO: Check if load balancer is deployed

        return JsonResponse({'redirect_url': get_url_from_status(client)})
    return render(request, 'load_balancer.html', context)
