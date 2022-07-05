from django.urls import reverse
from tesla_ce_supervisor.lib.client import SupervisorClient


# Create your views here.
def get_url_from_status(client: SupervisorClient) -> str:
    """
        Return the url to continue with the deployment process
        :param client: TeSLA CE Client instance
        :return: New url
    """
    status = client.tesla.get("DEPLOYMENT_STATUS")
    if status == 0: # START
        new_url = reverse('setup_home')
    elif status == 1:  # Deployment environment configuration
        new_url = reverse('setup_environment')
    elif status == 2:  # TeSLA Basic Information
        new_url = reverse('setup_tesla_basic_info')
    elif status == 3:  # Load Balancer deployment
        new_url = reverse('setup_load_balancer')
    elif status == 4:  # Setup external services
        new_url = reverse('setup_services_config')
    elif status == 5:  # Deploy services
        new_url = reverse('setup_services_deploy')
    elif status == 6:  # Register external services
        new_url = reverse('setup_services_register')
    elif status == 7:   # Deploy supervisor
        new_url = reverse('setup_supervisor')
    elif status == 8:  # Configuration wizard 1
        new_url = reverse('setup_step1')
    else:
        new_url = reverse('setup_home')
    return new_url
