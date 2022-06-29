import os
import filecmp
import shutil
import logging

from django.conf import settings
from tesla_ce_supervisor.lib.client import SupervisorClient
from tesla_ce_supervisor.lib.tesla.conf import Config

logger = logging.getLogger('main_background_loop')


def main_background_loop():
    logger.info('Main background loop running...')


