from django.http import JsonResponse
from django.shortcuts import render

from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status
from tesla_ce_supervisor.apps.web.forms.tesla_basics import TeslaBasicInfoForm


def tesla_basic_info(request):
    client = SupervisorClient.get_instance()

    form = TeslaBasicInfoForm()
    form.load_config(client.tesla.get_config())
    if client.tesla.get("DEPLOYMENT_SERVICES"):
        options_mode = 'development'
    else:
        options_mode = 'production'
    context = {
        'options': {
            'setup_status': client.tesla.get("DEPLOYMENT_STATUS"),
            'mode': options_mode
        },
        'form': form,
    }

    if request.method == 'POST':
        form = TeslaBasicInfoForm(request.POST)
        if form.is_valid():
            form.update_config(client.tesla.get_config())
            client.tesla.get_config().set('DEPLOYMENT_STATUS', 3)
            client.tesla.persist_configuration()
            return JsonResponse({'redirect_url': get_url_from_status(client)})
        return JsonResponse({'errors': form.errors})
    return render(request, 'basic_info.html', context)
