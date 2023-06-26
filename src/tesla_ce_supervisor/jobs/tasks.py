import os
import filecmp
import shutil
import logging

from django.conf import settings

logger = logging.getLogger('main_background_loop')


def main_background_loop():
    try:
        from tesla_ce_supervisor.lib.client import SupervisorClient
        from tesla_ce_supervisor.lib.tesla.conf import Config
        logger.info('Main background loop running...')

        # todo: check version file version VS db version

        # todo: update system status (service_status model in db):
        #   - check vault
        #   - check database
        #   - check redis
        #   - check rabbitmq
        #   - check minio
        #   - check supervisor

    except Exception:
        logger.error('Something goes wrong...')



