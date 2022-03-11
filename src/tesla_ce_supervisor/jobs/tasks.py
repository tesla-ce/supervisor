import os
import filecmp
import shutil
import logging

from django.core.management import call_command
from tesla_ce_supervisor.lib.client import SupervisorClient

logger = logging.getLogger(__name__)


def update_deploy_status():
    logger.debug('Update deploy status')
    client = SupervisorClient()

    # If configuration file does not exist, create it
    if not client.configuration_exists():
        logger.warning('Configuration file does not exist. Creating new configuration file.')
        client.export_configuration()
        logger.info('Configuration file created')

    # Check configuration
    errors = client.check_configuration()
    if not errors['valid']:
        logger.error('Configuration file not valid. Stop process. \n{}'.format('\n'.join(errors['errors'])))
        return
    if len(errors['warnings']) > 0:
        logger.warning('The following warnings were found checking configuration:\n{}'.format(
            '\n'.join(errors['warnings'])))

    # Check if configuration file has changed
    configuration_changed = False
    if os.path.exists('tesla-ce.cfg'):
        # Compare both files
        if not filecmp.cmp('tesla-ce.cfg', client.get_config_path()):
            logger.warning('External configuration differs from internal configuration.')
            configuration_changed = True
    else:
        logger.warning('Internal configuration file does not exist. External file is imported.')
        configuration_changed = True

    # Update configuration if needed
    if configuration_changed:
        logger.warning('Configuration changed. Reconfiguring TeSLA CE')
        shutil.copy(client.get_config_path(), 'tesla-ce.cfg')
        call_command('reconfigure')
