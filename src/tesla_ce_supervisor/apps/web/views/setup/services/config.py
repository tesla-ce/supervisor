from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status
from tesla_ce_supervisor.apps.web.forms.base import ConfigForm
from tesla_ce_supervisor.apps.web.forms.environment import NomadConsulForm, SwarmForm
from tesla_ce_supervisor.apps.web.forms.tesla_basics import TeslaBasicInfoForm

def service_configuration(request):
    client = SupervisorClient.get_instance()

    context = {
        'options': {
            'setup_status': client.tesla.get("DEPLOYMENT_STATUS"),
        },
    }

    if request.method == 'POST':
        # client.tesla.get_config().set('DEPLOYMENT_STATUS', 6)
        # client.tesla.persist_configuration()
        # return JsonResponse({'redirect_url': get_url_from_status(client)})
        return JsonResponse({'errors': {}})
    return render(request, 'services/config_services.html', context)
