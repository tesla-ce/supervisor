from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from tesla_ce_supervisor.lib.tesla import TeslaClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status
from tesla_ce_supervisor.apps.web.forms.base import ConfigForm
from tesla_ce_supervisor.apps.web.forms.environment import NomadConsulForm, SwarmForm
from tesla_ce_supervisor.apps.web.forms.tesla_basics import TeslaBasicInfoForm

def service_deployment(request):
    client = TeslaClient()
    client.get_config_path()
    client.load_configuration()

    form = TeslaBasicInfoForm()
    form.load_config(client.get_config())

    context = {
        'options': {
            'setup_status': client.get("DEPLOYMENT_STATUS"),
        },
        'form': form,
    }

    if request.method == 'POST':
        form = TeslaBasicInfoForm(request.POST)
        if form.is_valid():
            form.update_config(client.get_config())
            client.get_config().set('DEPLOYMENT_STATUS', 3)
            client.persist_configuration()
            return JsonResponse({'redirect_url': get_url_from_status(client)})
        return JsonResponse({'errors': form.errors})
    return render(request, 'basic_info.html', context)
