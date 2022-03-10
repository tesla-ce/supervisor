from django.conf import settings
from tesla_ce.lib import ConfigManager


def check_configuration():

    manager = ConfigManager(False)

    a = 3
