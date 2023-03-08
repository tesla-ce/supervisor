from django.http import JsonResponse
from django.shortcuts import render

from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status


def lb_view(request):
    client = SupervisorClient.get_instance()

    options_env = None
    if client.tesla.get("DEPLOYMENT_CATALOG_SYSTEM") == 'consul' and client.tesla.get("DEPLOYMENT_ORCHESTRATOR") == 'nomad':
        options_env = 'nomad_consul'
    elif client.tesla.get("DEPLOYMENT_CATALOG_SYSTEM") == 'swarm' and client.tesla.get("DEPLOYMENT_ORCHESTRATOR") == 'swarm':
        options_env = 'swarm'
    if client.tesla.get("DEPLOYMENT_SERVICES"):
        options_mode = 'development'
    else:
        options_mode = 'production'

    # Set Traefik as the load balancer for this deployment
    client.tesla.get_config().set("DEPLOYMENT_LB", 'traefik')
    client.tesla.persist_configuration()

    context = {
        'options': {
            'environment': options_env,
            'mode': options_mode,
            'catalog': client.tesla.get_config().get("DEPLOYMENT_CATALOG_SYSTEM"),
            'load_balancer': client.tesla.get_config().get("DEPLOYMENT_LB"),
            'base_domain': client.tesla.get_config().get("TESLA_DOMAIN"),
            'data_path': client.tesla.get_config().get("DEPLOYMENT_DATA_PATH"),
        }
    }
    if request.method == 'POST':
        lb_status = client.check_lb()
        if lb_status.is_valid():
            if client.tesla.get("DEPLOYMENT_SERVICES"):
                # Configuration will be generated as part of the deployment
                client.tesla.get_config().set('DEPLOYMENT_STATUS', 5)
            else:
                client.tesla.get_config().set('DEPLOYMENT_STATUS', 4)
            client.tesla.persist_configuration()
            return JsonResponse({'redirect_url': get_url_from_status(client)})
        return JsonResponse({'errors': lb_status.to_json()})
    return render(request, 'load_balancer.html', context)
