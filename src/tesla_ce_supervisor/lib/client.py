import datetime
import json
import os
import typing
import socket
import requests
import psycopg2
import MySQLdb
import botocore
import boto3


from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature

from .catalog import CatalogClient
from .tesla import TeslaClient
from .tesla.vault.manager import VaultManager, ConnectionError
from .tesla.exceptions import TeslaVaultException
from .deploy import DeployClient
from .setup import SetupClient
from .task import TaskClient
from .models.check import ServiceStatus, ConnectionStatus
from tesla_ce_supervisor.apps.api.models import SystemStatus, SYSTEM_STATUS
from typing import Optional

_client_instance: Optional['SupervisorClient'] = None


class SupervisorClient:
    @staticmethod
    def get_instance() -> 'SupervisorClient':
        global _client_instance
        if _client_instance is None:
            _client_instance = SupervisorClient()

        return _client_instance

    def __init__(self):
        self._tesla = TeslaClient()
        self._tesla.get_config_path()
        self._tesla.load_configuration()
        self._catalog = CatalogClient(self._tesla.get_config())
        self._deploy = DeployClient(self._tesla.get_config())
        self._task = TaskClient()
        self.supervisor_service_access_token = None

    @property
    def tesla(self):
        return self._tesla

    @property
    def catalog(self):
        return self._catalog

    @property
    def deploy(self):
        return self._deploy

    @property
    def task(self):
        return self._task

    def get_services(self):
        return self._catalog.get_services()

    def configuration_exists(self):
        return self._tesla.configuration_exists()

    def check_configuration(self):
        return self._tesla.check_configuration()

    def export_configuration(self):
        return self._tesla.export_configuration()

    def load_configuration(self):
        return self._tesla.load_configuration()

    def get_config_path(self):
        return self._tesla.get_config_path()

    def check_services(self):

        status = {
            # Check Database
            'db': self.check_database(),
            # Check Vault
            'vault': self.check_vault(),
            # Check MinIO
            'minio': self.check_minio(),
            # Check Redis
            'redis': self.check_redis(),
            # Check RabbitMQ
            'rabbitmq': self.check_rabbitmq(),
        }
        all_ok = True
        errors = []
        for srv in status:
            if not status[srv].is_valid():
                all_ok = False
                errors.append(status[srv].to_json())

        return {
            'valid': all_ok,
            'status': status,
            'errors': errors
        }

    def auto_deploy(self):
        # load config from env
        # write config file
        # deploy LB?
        # deploy services?
        # setup vault
        # deploy core
        # deploy dashboard

        # deploy VLE?

        # deploy providers? info in env variable.

        # todo: implement this with exit()
        # todo: write file log
        pass

    def get_vault_configuration(self) -> dict:
        """
            Get the list of Vault configuration files to be exported or executed
            :return: Dictionary with all required files and content for each file
        """
        return {
            'tesla-ce-policies.hcl': self._tesla.get_vault_policies(),
        }

    def setup_vault(self) -> None:
        """
            Run Vault configuration
        """
        pass

    def get_deployer(self,
                     target: typing.Optional[typing.Union[typing.Literal["NOMAD"], typing.Literal["SWARM"]]] = None
                     ) -> DeployClient:
        """
            Create a deployer instance using current configuration
            :param target: The target system (Nomad or Swarm)
            :return: Deployer instance
        """
        self.tesla.get_config_path()
        self.tesla.load_configuration()

        return DeployClient(self.tesla.get_config(), target)

    def get_setup(self):
        """
            Create a setup instance using current configuration
            :return: SetupClient instance
        """
        return SetupClient(self._tesla.get_config())

    def check_dns(self, hostname: typing.Optional[str] = None) -> dict:
        """
            Check if a hostname is registered can be resolved.
            :param hostname: The hostname to test. If not provided, all required hostnames are checked.
            :return: Resolution information
        """
        if hostname is None:
            # Get domain
            base_domain = self._tesla.get_config().get('TESLA_DOMAIN')
            if base_domain is None:
                return {}
            # Return values for all required hostnames
            ret_val = {
                base_domain: self.check_dns(hostname=base_domain),
            }
            # If services are deployed, check services domains
            if self._tesla.get_config().get('DEPLOYMENT_SERVICES'):
                ret_val[f'vault.{base_domain}'] = self.check_dns(hostname=f'vault.{base_domain}')
                ret_val[f'storage.{base_domain}'] = self.check_dns(hostname=f'storage.{base_domain}')
                ret_val[f'rabbitmq.{base_domain}'] = self.check_dns(hostname=f'rabbitmq.{base_domain}')
                ret_val[f'supervisor.{base_domain}'] = self.check_dns(hostname=f'supervisor.{base_domain}')
        else:
            try:
                ip = socket.gethostbyname(hostname)
                ret_val = {
                    'valid': True,
                    'hostname': hostname,
                    'ip': ip,
                    'error': None
                }
            except socket.gaierror as err:
                ret_val = {
                    'valid': False,
                    'hostname': hostname,
                    'ip': None,
                    'error': err.__str__()
                }

        return ret_val

    def check_lb(self) -> ServiceStatus:
        """
            Check deployment status of the load balancer
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('LB'),
            self._catalog.get_lb_status()
        )

        return status

    def check_database(self) -> ServiceStatus:
        """
            Check deployment status of the database
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('DATABASE'),
            self._catalog.get_database_status()
        )

        return status

    def check_minio(self) -> ServiceStatus:
        """
            Check deployment status of MinIO
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('MINIO'),
            self._catalog.get_minio_status()
        )

        return status

    def check_redis(self) -> ServiceStatus:
        """
            Check deployment status of Redis
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('REDIS'),
            self._catalog.get_redis_status()
        )

        return status

    def check_rabbitmq(self) -> ServiceStatus:
        """
            Check deployment status of RabbitMQ
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('RABBITMQ'),
            self._catalog.get_rabbitmq_status()
        )

        return status

    def check_vault(self) -> ServiceStatus:
        """
            Check deployment status of Vault
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('VAULT'),
            self._catalog.get_vault_status()
        )

        return status

    def check_supervisor(self) -> ServiceStatus:
        """
            Check deployment status of TeSLA CE Supervisor
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('SUPERVISOR'),
            self._catalog.get_supervisor_status()
        )

        return status

    def check_api(self) -> ServiceStatus:
        """
            Check deployment status of API
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('API'),
            self._catalog.get_api_status()
        )

        return status

    def check_beat(self) -> ServiceStatus:
        """
            Check deployment status of API
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('BEAT'),
            self._catalog.get_beat_status()
        )

        return status

    def check_workers_module(self, module) -> ServiceStatus:
        """
            Check deployment status of API
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status(module),
            self._catalog.get_workers_status(module)
        )

        return status

    def check_lapi(self) -> ServiceStatus:
        """
            Check deployment status of API
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('LAPI'),
            self._catalog.get_lapi_status()
        )

        return status

    def check_dashboard(self) -> ServiceStatus:
        """
            Check deployment status of Dashboard
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('DASHBOARD'),
            self._catalog.get_dashboard_status()
        )

        return status

    def check_moodle(self) -> ServiceStatus:
        """
            Check deployment status of Dashboard
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('MOODLE'),
            self._catalog.get_moodle_status()
        )

        return status

    def check_tks(self) -> ServiceStatus:
        """
            Check deployment status of Dashboard
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('TKS'),
            self._catalog.get_tks_status()
        )

        return status

    def check_tfr(self) -> ServiceStatus:
        """
            Check deployment status of Dashboard
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('TFR'),
            self._catalog.get_tfr_status()
        )

        return status

    def check_tpt(self) -> ServiceStatus:
        """
            Check deployment status of Dashboard
            :return: Status information
        """
        status = ServiceStatus(
            self.get_deployer().get_status('TPT'),
            self._catalog.get_tpt_status()
        )

        return status

    def check_module(self, module: str) -> ServiceStatus:
        module = module.upper()
        if module == 'SUPERVISOR':
            return self.check_supervisor().to_json()
        elif module == 'VAULT':
            return self.check_vault().to_json()
        elif module == 'RABBITMQ':
            return self.check_rabbitmq().to_json()
        elif module == 'REDIS':
            return self.check_redis().to_json()
        elif module == 'MINIO':
            return self.check_minio().to_json()
        elif module == 'DATABASE':
            return self.check_database().to_json()
        elif module == 'LB':
            return self.check_lb().to_json()
        elif module == 'DNS':
            return self.check_dns()
        elif module == 'API':
            return self.check_api().to_json()
        elif module == 'BEAT':
            return self.check_beat().to_json()
        elif module.upper() in ["WORKER-ALL", "WORKER-ENROLMENT", "WORKER-ENROLMENT-STORAGE",
                                "WORKER-ENROLMENT-VALIDATION", "WORKER-VERIFICATION", "WORKER-ALERTS",
                                "WORKER-REPORTING"]:
            return self.check_workers_module(module.upper()).to_json()

        elif module == 'LAPI':
            return self.check_lapi().to_json()
        elif module == 'DASHBOARD':
            return self.check_dashboard().to_json()
        elif module == 'MOODLE':
            return self.check_moodle().to_json()
        elif module == 'TFR':
            return self.check_tfr().to_json()
        elif module == 'TKS':
            return self.check_tks().to_json()
        elif module == 'TPT':
            return self.check_tpt().to_json()



    def check_connection(self, module: str) -> ConnectionStatus:
        """
            Check connection status of module
            :return: ConnectionStatus
        """
        if module.upper() == 'SWARM':
            status = SwarmDeployer(config=self.tesla.get_config()).check_connection(module)

        elif module.upper() == 'NOMAD':
            status = NomadDeployer(config=self.tesla.get_config()).check_connection(module)

        elif module.upper() == 'CONSUL':
            status = ConsulCatalog(config=self.tesla.get_config()).check_connection(module)

        return status

    def make_request_to_supervisor_service(self, method, url, data):
        if self.supervisor_service_access_token is None:
            auth_url = '{}/supervisor/api/token/'.format(self.get_supervisor_url())

            data_auth = {
                'username': self.tesla.get_config().get('SUPERVISOR_ADMIN_USER'),
                'password': self.tesla.get_config().get('SUPERVISOR_ADMIN_PASSWORD')
            }
            headers = {
                'Content-type': 'application/json'
            }
            auth_response = requests.post(url=auth_url, data=json.dumps(data_auth), verify=False, headers=headers)

            if auth_response.status_code == 200:
                self.supervisor_service_access_token = json.loads(auth_response.content)

        if self.supervisor_service_access_token is not None:
            headers = {
                'Content-type': 'application/json',
                'Authentication': 'JWT {}'.format(self.supervisor_service_access_token['access'])
            }

            url = '{}{}'.format(self.get_supervisor_url(), url)

            response = requests.request(method=method, url=url, data=json.dumps(data), headers=headers, verify=False)

            return response

    def use_https(self):
        # todo
        pass

    def configure_service(self, module: str, request: dict):
        config = request.data.get('config')
        module = module.upper()
        result = False
        info = []

        if module == 'SUPERVISOR':
            supervisor_status = SystemStatus()
            # INITIALIZING
            supervisor_status.status = SYSTEM_STATUS[1][0]
            supervisor_status.save()

            for section in config:
                for item_key in config[section]:
                    config_key = "{}_{}".format(section, item_key).upper()
                    if config[section][item_key]['value'] is not None:
                        self.tesla.get_config().set(config_key, config[section][item_key]['value'])

            self.tesla.persist_configuration(force_db=True)

            # put status initializer
            supervisor_status.status = SYSTEM_STATUS[2][0]
            supervisor_status.last_config = datetime.datetime.now()
            supervisor_status.save()
            result = True

        elif module == 'DATABASE':
            # try to connect with root user
            # create database
            db_name = self.tesla.get_config().get('db_name')
            db_host = self.tesla.get_config().get('db_host')
            db_port = self.tesla.get_config().get('db_port')
            db_user = self.tesla.get_config().get('db_user')
            db_password = self.tesla.get_config().get('db_user')

            if self.tesla.get_config().get('db_engine') == 'mysql':
                try:
                    conn = MySQLdb.connect(
                        host=db_host,
                        port=db_port,
                        user=self.tesla.get_config().get('db_root_user'),
                        password=self.tesla.get_config().get('db_root_password'),
                        connect_timeout=5
                    )
                    cursor = conn.cursor()
                except MySQLdb.Error as err:
                    pass

                # create database
                try:
                    cursor.execute('CREATE DATABASE IF NOT EXISTS {};'.format(db_name))
                except MySQLdb.Error as err:
                    pass

                # create user and grant permissions
                try:
                    cursor.execute('GRANT ALL PRIVILEGES ON {}.* TO \'{}\'@\'%\' IDENTIFIED BY \'{}\';'.format(
                        db_name,
                        db_user,
                        db_password
                    ))
                except MySQLdb.Error as err:
                    pass

                # flush all
                try:
                    cursor.execute('FLUSH PRIVILEGES;')
                except MySQLdb.Error as err:
                    pass

                try:
                    conn.commit()
                    cursor.close()
                    conn.close()
                except MySQLdb.Error as err:
                    pass

            elif self.tesla.get_config().get('db_engine') == 'postgresql':
                try:
                    conn = psycopg2.connect(
                        host=db_host,
                        port=db_port,
                        user=self.tesla.get_config().get('db_root_user'),
                        password=self.tesla.get_config().get('db_root_password'),
                        connect_timeout=5
                    )
                    cursor = conn.cursor()

                except psycopg2.Error as err:
                    pass

                # create database
                try:
                    cursor.execute(
                        'SELECT \'CREATE DATABASE {}\' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = \'{}\')\\gexec'.format(
                            db_name, db_name)
                    )
                except MySQLdb.Error as err:
                    pass

                # create user
                try:
                    cursor.execute("CREATE USER {} WITH ENCRYPTED PASSWORD '{}';".format(
                        db_user,
                        db_password
                    ))
                except MySQLdb.Error as err:
                    pass

                # grant permissions
                try:
                    cursor.execute('GRANT ALL PRIVILEGES ON DATABASE {} TO {};'.format(
                        db_name,
                        db_user
                    ))
                except MySQLdb.Error as err:
                    pass

                try:
                    conn.commit()
                    cursor.close()
                    conn.close()
                except MySQLdb.Error as err:
                    pass
            result = True

        elif module == 'MINIO':
            # check if buckets are created
            try:
                s3 = boto3.client('s3',
                                  endpoint_url=self.tesla.get_config().get('STORAGE_URL'),
                                  aws_access_key_id=self.tesla.get_config().get('STORAGE_ACCESS_KEY'),
                                  aws_secret_access_key=self.tesla.get_config().get('STORAGE_SECRET_KEY'),
                                  aws_session_token=None,
                                  region_name=self.tesla.get_config().get('STORAGE_REGION'),
                                  config=boto3.session.Config(signature_version='s3v4'),
                                  #verify=self.config.get('STORAGE_SSL_VERIFY')
                                  verify=False
                                  )

                # check if tesla bucket is created
                tesla_name_bucket = self.tesla.get_config().get('STORAGE_BUCKET_NAME')
                tesla_public_name_bucket = self.tesla.get_config().get('STORAGE_PUBLIC_BUCKET_NAME')
                region = self.tesla.get_config().get('STORAGE_REGION')

                tesla_bucket = None
                tesla_public_bucket = None

                buckets = s3.list_buckets()
                if len(buckets.get('Buckets')) > 0:
                    for bucket in buckets.get('Buckets'):
                        if bucket.get('Name') == tesla_name_bucket:
                            tesla_bucket = bucket
                        elif bucket.get('Name') == tesla_public_name_bucket:
                            # todo: check if this bucket has public policy
                            tesla_public_bucket = bucket

                if tesla_bucket is None:
                    s3.create_bucket(ACL='private', Bucket=tesla_name_bucket, CreateBucketConfiguration={'LocationConstraint': region})

                if tesla_public_bucket is None:
                    s3.create_bucket(ACL='public', Bucket=tesla_public_name_bucket, CreateBucketConfiguration={'LocationConstraint': region})

                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                            "Resource": ["arn:aws:s3:::{}".format(tesla_public_name_bucket)],
                        },
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetObject"],
                            "Resource":
                                ["arn:aws:s3:::{}/*".format(tesla_public_name_bucket)]
                        },
                    ],
                }

                s3.put_bucket_policy(Bucket=tesla_public_name_bucket, Policy=json.dumps(policy))
                s3.get_bucket_policy(Bucket=tesla_public_name_bucket)
                result = True

            except botocore.exceptions.BotoCoreError as err:
                info = str(err)

        elif module == 'VAULT':
            try:
                vault_manager = VaultManager(self.tesla.get_config())
                vault_manager.test_connection()
                if vault_manager.is_ready() is False:
                    vault_manager.initialize_without_setup()

                result = vault_manager.is_ready()
                if result is True:
                    self.tesla.persist_configuration()
                    supervisor_status = SystemStatus()
                    supervisor_status.status = SYSTEM_STATUS[3][0]
                    supervisor_status.last_config = datetime.datetime.now()
                    supervisor_status.save()

            except (TeslaVaultException, ConnectionError) as err:
                info = str(err)

        elif module == 'TESLA':
            step = request.data.get('step')
            token = self.get_api_signed_token()

            url = self.get_supervisor_url()
            # todo: remove this line
            url = 'http://localhost:8081'

            command = '/venv/bin/tesla_ce remote_setup --command={}'.format(step)
            environment = {
                'SUPERVISOR_REMOTE_URL': '{}/supervisor/api/admin/config/?token={}'.format(url, token)
            }
            command_status = self.deploy.execute_command_inside_container('API', command, environment)
            result = command_status.status
            info = command_status.info

        self.tesla.load_configuration()

        return {"result": result, "info": info}

    def supervisor_status(self):
        try:
            system_status = SystemStatus.objects.get(id=1)
            system_status = system_status.to_json()

        except ObjectDoesNotExist:
            system_status = {}

        return system_status

    def get_api_signed_token(self):
        signer = TimestampSigner()
        return signer.sign(self.tesla.get_config().get_uuid())

    def check_api_signed_token(self, token, max_age=3600):
        try:
            signer = TimestampSigner()
            signer.unsign(token, max_age=max_age)
            return True
        except (SignatureExpired, BadSignature) as err:
            pass

        return False

    def get_supervisor_url(self):
        # todo modify this server
        if settings.SETUP_MODE == 'DEV':
            return 'http://localhost:8081'

        return "https://{}".format(self.tesla.get_config().get('TESLA_DOMAIN'))

    def register_provider(self, module):
        instruments_acronym = {"TFR": "fr", "TPT": "plag", "TKS": "ks", "TFA": "fa", "TVR": "vr"}
        selected_instrument_acronym = instruments_acronym.get(module.upper())

        domain = self.tesla.get_config().get('tesla_domain')
        user = self.tesla.get_config().get('tesla_admin_mail')
        password = self.tesla.get_config().get('tesla_admin_password')
        url = "https://{}/api/v2/auth/login".format(domain)

        data = {
            'email': user,
            'password': password
        }
        verify_ssl = True

        if settings.DEBUG is True:
            verify_ssl = False
        response = requests.post(url, data, verify=verify_ssl)
        access_tokens = response.json()

        headers = {"Authorization": "JWT {}".format(access_tokens.get('token').get('access_token'))}
        # check if provider is registered

        url = "https://{}/api/v2/admin/instrument/".format(domain)
        response = requests.get(url, data, verify=verify_ssl, headers=headers)
        aux = response.json()
        instruments = aux.get('results')

        instrument_id = None

        for instrument in instruments:
            if selected_instrument_acronym == instrument.get('acronym'):
                instrument_id = instrument.get('id')

                url = 'https://{}/api/v2/admin/instrument/{}/provider/'.format(domain, instrument_id)
                response = requests.get(url, verify=verify_ssl, headers=headers)
                aux = response.json()
                providers = aux.get('results')
                provider_found = False
                if providers:
                    for prov in providers:
                        if prov.get('acronym') == module.lower():
                            url = 'https://{}/api/v2/admin/instrument/{}/provider/{}/'.format(domain, instrument_id, prov.get('id'))
                            response = requests.delete(url, headers=headers, verify=verify_ssl)
                            # provider_found = True

                if not provider_found:
                    # download json of instrument
                    response = requests.get('https://raw.githubusercontent.com/tesla-ce/core/main/providers/{}_{}.json'.
                                            format(selected_instrument_acronym, module.lower()), headers=headers,
                                            verify=verify_ssl)

                    provider_json = response.json()
                    # Register a FR provider
                    provider_json['enabled'] = True
                    provider_json['validation_active'] = True

                    if 'instrument' in provider_json:
                        del provider_json['instrument']

                    url = 'https://{}/api/v2/admin/instrument/{}/provider/'.format(domain, instrument_id)

                    provider_register = requests.post(url, json=provider_json, headers=headers, verify=verify_ssl)

                    url = 'https://{}/api/v2/admin/instrument/{}/'.format(domain, instrument_id)
                    fr_inst_enable_resp = requests.patch(url, json={'enabled': True}, headers=headers,
                                                         verify=verify_ssl)

        pass


