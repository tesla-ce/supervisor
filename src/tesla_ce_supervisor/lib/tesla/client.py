import os
import configparser
from django.conf import settings
from .conf import Config
from .vault import VaultManager


class TeslaClient:

    def __init__(self):
        self._config = Config()
        self._config_file = os.path.join(settings.DATA_DIRECTORY, 'tesla-ce.cfg')
        self._secrets_path = os.environ.get('SECRETS_PATH', '/var/run/secrets')

    def get(self, key, default=None):
        """
            Get configuration value
            :param key: Configuration key
            :param default: Default value in case it is not found
            :return: Value
        """
        # Check if value is provided as environment variable
        if key in os.environ:
            return os.environ[key]
        secret_path = os.path.join(self._secrets_path, key)
        if os.path.exists(secret_path):
            with open(secret_path, 'r') as secret_file:
                return secret_file.read()
        return self._config.get(key, default)

    def configuration_exists(self):
        """
            Check if configuration file exists
            :return: True if it exists or False otherwise
        """
        return os.path.exists(self._config_file)

    def load_env_configuration(self):
        """
            Load configuration from provided environment variables and secrets
        """
        self._config = Config()
        keys = self._config.get_config_kv().keys()
        for key in keys:
            value = self.get(key)
            self._config.set(key, value)

    def check_configuration(self):
        """
            Check if configuration is valid
            :return: Dictionary with errors
        """
        errors = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "error_missing": [],
            "warning_missing": [],
        }
        if not self.configuration_exists():
            errors['valid'] = False
            errors['errors'].append('Missing configuration file: {}'.join(self._config_file))
            return errors

        # Load the configuration file
        if not self.load_configuration():
            errors['valid'] = False
            errors['errors'].append('Error loading configuration configuration file: {}'.join(self._config_file))
            return errors

        # Check required parameters are provided
        # TeSLA
        if self._config.get('TESLA_DOMAIN') is None:
            errors['error_missing'].append('TESLA_DOMAIN')
        if self._config.get('TESLA_ADMIN_MAIL') is None:
            errors['error_missing'].append('TESLA_ADMIN_MAIL')
        # Database
        if self._config.get('DB_USER') is None:
            errors['error_missing'].append('DB_USER')
        if self._config.get('DB_PASSWORD') is None:
            errors['error_missing'].append('DB_PASSWORD')
        if self._config.get('DB_ROOT_PASSWORD') is None:
            errors['warning_missing'].append('DB_ROOT_PASSWORD')
        # Vault
        if self._config.get('VAULT_TOKEN') is None:
            errors['warning_missing'].append('VAULT_TOKEN')
        if self._config.get('VAULT_KEYS') is None:
            errors['warning_missing'].append('VAULT_KEYS')
        # Redis
        if self._config.get('REDIS_PASSWORD') is None:
            errors['error_missing'].append('REDIS_PASSWORD')
        # Storage
        if self._config.get('STORAGE_ACCESS_KEY') is None:
            errors['error_missing'].append('STORAGE_ACCESS_KEY')
        if self._config.get('STORAGE_SECRET_KEY') is None:
            errors['error_missing'].append('STORAGE_SECRET_KEY')
        # RabbitMQ
        if self._config.get('RABBITMQ_ADMIN_USER') is None:
            errors['error_missing'].append('RABBITMQ_ADMIN_USER')
        if self._config.get('RABBITMQ_ADMIN_PASSWORD') is None:
            errors['error_missing'].append('RABBITMQ_ADMIN_PASSWORD')
        # DJango
        if self._config.get('DJANGO_SECRET_KEY') is None:
            errors['error_missing'].append('DJANGO_SECRET_KEY')

        # Build final structure
        if len(errors['error_missing']) > 0:
            errors['errors'].append('Missing configuration value for fields: [{}]'.format(
                ', '.join(errors['error_missing']))
            )
        if len(errors['warning_missing']) > 0:
            errors['warnings'].append('Missing configuration value for fields: [{}]'.format(
                ', '.join(errors['warning_missing']))
            )
        errors['valid'] = len(errors['errors']) == 0

        return errors

    def export_configuration(self):
        """
            Save current configuration to the configuration file
        """
        # Load configuration from environment
        self.load_env_configuration()

        # Write configuration to disk
        with open(self._config_file, 'w') as conf_fh:
            self._config.write(conf_fh)
        # Change permissions to the file
        os.chmod(self._config_file, 0o600)

    def load_configuration(self):
        if settings.SETUP_MODE in ('SETUP', 'DEV'):
            if os.path.exists(self._config_file):
                conf = configparser.ConfigParser()
                with open(self._config_file, 'r') as conf_file:
                    conf.read_file(conf_file, self._config_file)
                    self._config.update(conf)

                self._config.set('tesla_config_file', self._config_file)
                self._config.get_effective_config()
            else:
                return False
            return True
        else:
            self._config.load_db()
            return True

    def get_config_path(self):
        """
            Get the path to the configuration file
            :return: Configuration file path
        """
        return self._config_file

    def persist_configuration(self, force_db=False):
        """
            Write configuration data to disk
        """
        if settings.SETUP_MODE in ('SETUP', 'DEV'):
            with open(os.path.join(self.get_config_path()), 'w') as config_file:
                self._config.write(config_file)
        else:
            self._config.persist_db()

        if force_db is True:
            self._config.persist_db()

    def check_vault_status(self):
        self._config.set('VAULT_MANAGEMENT', True)
        return VaultManager(self._config).check_vault_status()

    def get_vault_policies(self):
        self._config.set('VAULT_MANAGEMENT', True)
        policies = VaultManager(self._config).get_policies_definition()
        return policies

    def get_config(self):
        return self._config

    def get_module_credentials(self, module):
        self._config.set('VAULT_MANAGEMENT', True)
        vault_client = VaultManager(self._config)

        return vault_client.get_module_credentials(module)

    def get_version(self):
        """
            Get current version
            :return: Version value
        """
        version_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'VERSION'))
        with open(version_file, 'r') as v_file:
            version = v_file.read()
        version = version.strip()
        return version

    def create_module_entity_manual(self, module, extra_data=None, module_name=None):
        self._config.set('VAULT_MANAGEMENT', True)
        vault_client = VaultManager(self._config)

        return vault_client.create_module_entity_manual(module, extra_data, module_name)