from django.http import JsonResponse
from django.shortcuts import render

from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status


def service_deployment(request):
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

    context = {
        'options': {
            'environment': options_env,
            'mode': options_mode,
            'catalog': client.tesla.get("DEPLOYMENT_CATALOG_SYSTEM"),
            'data_path': client.tesla.get("DEPLOYMENT_DATA_PATH"),
        },
    }

    if request.method == 'POST':
        services_status = client.check_services()
        if services_status['valid']:
            client.tesla.get_config().set('DEPLOYMENT_STATUS', 7)
            client.tesla.persist_configuration()
            return JsonResponse({'redirect_url': get_url_from_status(client)})
        return JsonResponse({'errors': services_status['errors']})
    return render(request, 'services/deploy_services.html', context)
