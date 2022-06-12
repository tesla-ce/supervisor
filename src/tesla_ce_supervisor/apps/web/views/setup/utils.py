from django.urls import reverse
from tesla_ce_supervisor.lib.tesla import TeslaClient


# Create your views here.
def get_url_from_status(client: TeslaClient) -> str:
    """
        Return the url to continue with the deployment process
        :param client: TeSLA CE Client instance
        :return: New url
    """
    status = client.get("DEPLOYMENT_STATUS")
    if status == 0: # START
        new_url = reverse('setup_home')
    elif status == 1:  # Deployment environment configuration
        new_url = reverse('setup_environment')
    elif status == 2:  # TeSLA Basic Information
        new_url = reverse('setup_tesla_basic_info')
    elif status == 3:  # Configuration wizard 1
        new_url = reverse('setup_step1')
    else:
        new_url = reverse('setup_home')
    return new_url
