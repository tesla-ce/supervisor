from django.http import JsonResponse
from django.shortcuts import render

from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status



def home(request):
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
            'setup_status': client.tesla.get("DEPLOYMENT_STATUS")
        }
    }
    if request.method == 'POST':
        if request.POST['action'] == 'start':
            if request.POST['environment'] == 'nomad_consul':
                client.tesla.get_config().set("DEPLOYMENT_CATALOG_SYSTEM", 'consul')
                client.tesla.get_config().set("DEPLOYMENT_ORCHESTRATOR", 'nomad')
            elif request.POST['environment'] == 'swarm':
                client.tesla.get_config().set("DEPLOYMENT_CATALOG_SYSTEM", 'swarm')
                client.tesla.get_config().set("DEPLOYMENT_ORCHESTRATOR", 'swarm')
            if request.POST['mode'] == 'development':
                client.tesla.get_config().set("DEPLOYMENT_SERVICES", True)
            elif request.POST['mode'] == 'production':
                client.tesla.get_config().set("DEPLOYMENT_SERVICES", False)
            client.tesla.get_config().set("DEPLOYMENT_STATUS", 1)
        elif request.POST['action'] == 'reset':
            client.tesla.get_config().set("DEPLOYMENT_STATUS", 0)
        elif request.POST['action'] == 'continue':
            # No additional action is required
            pass
        client.tesla.persist_configuration()
        return JsonResponse({'redirect_url': get_url_from_status(client)})
    return render(request, 'home.html', context)
