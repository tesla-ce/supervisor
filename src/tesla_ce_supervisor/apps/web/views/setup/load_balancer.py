from django.http import JsonResponse
from django.shortcuts import render

from tesla_ce_supervisor.lib.tesla import TeslaClient
from tesla_ce_supervisor.lib.client import SupervisorClient
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
            'catalog': client.get("DEPLOYMENT_CATALOG_SYSTEM"),
            'load_balancer': client.get("DEPLOYMENT_LB"),
            'base_domain': client.get("TESLA_DOMAIN"),
        }
    }
    if request.method == 'POST':
        s_client = SupervisorClient()
        lb_status = s_client.check_lb()
        if lb_status.is_valid():
            if client.get("DEPLOYMENT_SERVICES"):
                # Configuration will be generated as part of the deployment
                client.get_config().set('DEPLOYMENT_STATUS', 5)
            else:
                client.get_config().set('DEPLOYMENT_STATUS', 4)
            client.persist_configuration()
            return JsonResponse({'redirect_url': get_url_from_status(client)})
        return JsonResponse({'errors': lb_status.to_json()})
    return render(request, 'load_balancer.html', context)
