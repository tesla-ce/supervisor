import os
import filecmp
import shutil
import logging

from django.conf import settings
from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.lib.tesla.conf import Config

logger = logging.getLogger('main_background_loop')


def main_background_loop():
    # If Supervisor is started in Configuration mode and
    if settings.SETUP_MODE.upper() == 'CONFIG' and os.path.exists(os.path.join(settings.SECRETS_PATH, 'TESLA_CE_CFG')):

        # Load configuration from secret
        conf = Config()
        conf.load_file(os.path.join(settings.SECRETS_PATH, 'TESLA_CE_CFG'))

        # Create or update configuration keys to local database
        conf.persist_db()


