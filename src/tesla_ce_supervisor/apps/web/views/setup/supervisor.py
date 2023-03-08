from django.http import JsonResponse
from django.shortcuts import render

from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status


def supervisor_view(request):
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

    context = {
        'options': {
            'environment': options_env,
            'mode': options_mode,
            'catalog': client.tesla.get("DEPLOYMENT_CATALOG_SYSTEM"),
            'load_balancer': client.tesla.get("DEPLOYMENT_LB"),
            'base_domain': client.tesla.get("TESLA_DOMAIN"),
            'data_path': client.tesla.get("DEPLOYMENT_DATA_PATH"),
            'services': ['supervisor', 'vault', 'database', 'rabbitmq', 'redis', 'minio']
        }
    }

    if client.tesla.get("SUPERVISOR_SECRET") is None:
        client.tesla.get_config().set("SUPERVISOR_SECRET", client.tesla.get_config().get_uuid())

    if client.tesla.get("SUPERVISOR_ADMIN_PASSWORD") is None:
        client.tesla.get_config().set("SUPERVISOR_ADMIN_PASSWORD", client.tesla.get_config().get_uuid())

    client.tesla.persist_configuration()

    if request.method == 'POST':
        # Configuration will be generated as part of the deployment
        client.tesla.get_config().set('DEPLOYMENT_STATUS', 8)
        client.tesla.persist_configuration()
        return JsonResponse({'redirect_url': get_url_from_status(client)})

    return render(request, 'supervisor.html', context)
