from django.http import JsonResponse
from django.shortcuts import render

from tesla_ce_supervisor.lib.tesla import TeslaClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status



def home(request):
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
            'setup_status': client.get("DEPLOYMENT_STATUS")
        }
    }
    if request.method == 'POST':
        if request.POST['action'] == 'start':
            if request.POST['environment'] == 'nomad_consul':
                client.get_config().set("DEPLOYMENT_CATALOG_SYSTEM", 'consul')
                client.get_config().set("DEPLOYMENT_ORCHESTRATOR", 'nomad')
            elif request.POST['environment'] == 'swarm':
                client.get_config().set("DEPLOYMENT_CATALOG_SYSTEM", 'swarm')
                client.get_config().set("DEPLOYMENT_ORCHESTRATOR", 'swarm')
            if request.POST['mode'] == 'development':
                client.get_config().set("DEPLOYMENT_SERVICES", True)
            elif request.POST['mode'] == 'production':
                client.get_config().set("DEPLOYMENT_SERVICES", False)
            client.get_config().set("DEPLOYMENT_STATUS", 1)
        elif request.POST['action'] == 'reset':
            client.get_config().set("DEPLOYMENT_STATUS", 0)
        elif request.POST['action'] == 'continue':
            # No additional action is required
            pass
        client.persist_configuration()
        return JsonResponse({'redirect_url': get_url_from_status(client)})
    return render(request, 'home.html', context)
