import base64
from django.http import JsonResponse
from django.shortcuts import render

from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.apps.web.views.setup.utils import get_url_from_status


def finished_view(request):
    client = SupervisorClient.get_instance()

    context = {
        'domain': client.tesla.get("TESLA_DOMAIN")
    }

    if request.method == 'POST':
        # Configuration will be generated as part of the deployment
        password = request.POST.get('pass')

        file = client.get_tesla_ce_zip(password)
        json_resp = {
            'zip': 'data:application/zip;base64,{}'.format(base64.b64encode(file).decode())
        }
        return JsonResponse(json_resp)

    return render(request, 'finished.html', context)
