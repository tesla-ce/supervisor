from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from tesla_ce_supervisor.lib.tesla import TeslaClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status
from tesla_ce_supervisor.apps.web.forms.base import ConfigForm
from tesla_ce_supervisor.apps.web.forms.environment import NomadConsulForm, SwarmForm
from tesla_ce_supervisor.apps.web.forms.tesla_basics import TeslaBasicInfoForm

def service_configuration(request):
    client = TeslaClient()
    client.get_config_path()
    client.load_configuration()

    context = {
        'options': {
            'setup_status': client.get("DEPLOYMENT_STATUS"),
        },
    }

    if request.method == 'POST':

        return JsonResponse({'errors': {}})
    return render(request, 'services/config_services.html', context)
