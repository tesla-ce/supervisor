import botocore
import boto3
import typing
import json
import redis
import pika
import psycopg2
import MySQLdb

from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
from storages.backends import s3boto3

from ..tesla.conf import Config
from ..tesla.vault.manager import VaultManager, ConnectionError
from ..tesla.exceptions import TeslaVaultException


class ServiceDeploymentInformation:
    def __init__(self, name: str,
                 orchestrator: typing.Optional[str] = None,
                 info: typing.Optional[dict] = None) -> None:
        super().__init__()

        self.name: str = name
        self.orchestrator: str = orchestrator
        self.jobs_expected: int = 0
        self.jobs_running: int = 0
        self.jobs_healthy: int = 0
        self.info: typing.Optional[dict] = info
        self.status: typing.Optional[typing.Union[typing.Literal['waiting'],
                                                  typing.Literal['success'],
                                                  typing.Literal['error']]] = None

    def is_valid(self) -> bool:
        return self.status == 'success'

    def get_jobs(self) -> dict:
        return {
            'expected': self.jobs_expected,
            'running': self.jobs_running,
            'healthy': self.jobs_healthy,
        }

    def to_json(self):
        info = None
        if self.info is not None:
            info = json.dumps(self.info)
        return {
            'name': self.name,
            'orchestrator': self.orchestrator,
            'jobs': self.get_jobs(),
            'status': self.status,
            'info': info
        }


class ServiceCatalogInformation:
    def __init__(self, name: str, catalog: typing.Optional[str]) -> None:
        super().__init__()

        self.name: str = name
        self.catalog: str = catalog
        self.instances_total: int = 0
        self.instances_healthy: int = 0
        self.services = []
        self.info: typing.Optional[dict] = None

    def is_healthy(self) -> bool:
        return self.instances_total == self.instances_healthy

    def get_instances(self):
        return {
                'total': self.instances_total,
                'healthy': self.instances_healthy
            }

    def to_json(self):
        info = None
        if self.info is not None:
            info = json.dumps(self.info)
        return {
            'name': self.name,
            'services': self.services,
            'instances': self.get_instances(),
            'healthy': self.is_healthy(),
            'info': info
        }


class ServiceStatus:
    def __init__(self,
                 deployment: typing.Optional[ServiceDeploymentInformation] = None,
                 catalog: typing.Optional[ServiceCatalogInformation] = None,
                 ) -> None:
        super().__init__()
        self.deploy_info: typing.Optional[ServiceDeploymentInformation] = deployment
        self.catalog_info: typing.Optional[ServiceCatalogInformation] = catalog

    def is_valid(self) -> bool:
        if self.deploy_info is None or self.catalog_info is None:
            return False
        return self.deploy_info.is_valid() and self.catalog_info.is_healthy()

    def get_jobs(self) -> dict:
        jobs = None
        if self.deploy_info is not None:
            jobs = self.deploy_info.get_jobs()
        return jobs

    def get_instances(self) -> dict:
        instances = None
        if self.catalog_info is not None:
            instances = self.catalog_info.get_instances()
            instances['services'] = self.catalog_info.services
        return instances

    def get_orchestrator(self) -> typing.Optional[str]:
        if self.deploy_info is not None:
            return self.deploy_info.orchestrator
        return None

    def get_catalog(self) -> typing.Optional[str]:
        if self.catalog_info is not None:
            return self.catalog_info.catalog
        return None

    def to_json(self):
        deploy_info = None
        if self.deploy_info is not None:
            deploy_info = self.deploy_info.to_json()
        catalog_info = None
        if self.catalog_info is not None:
            catalog_info = self.catalog_info.to_json()
        return {
            'orchestrator': self.get_orchestrator(),
            'catalog': self.get_catalog(),
            'instances': self.get_instances(),
            'jobs': self.get_jobs(),
            'valid': self.is_valid(),
            'info': {
                'deploy': deploy_info,
                'catalog': catalog_info
            }
        }


class ConnectionStatus:
    # valid: True|False
    # can connect?
    # info {
    #    "sealed"
    #    "auth"
    #    "init"...
    # }
    # errors {
    # }
    def __init__(self,
                 module: str,
                 config: typing.Optional[Config] = None
                 ) -> None:
        super().__init__()
        self.module = module
        self.config = config

    def status_vault(self):
        valid = False
        ready = False
        info = {}
        try:
            vault_manager = VaultManager(self.config)
            valid = vault_manager.test_connection()
            ready = vault_manager.is_ready()
        except (TeslaVaultException, ConnectionError, TypeError) as err:
            info = str(err)

        return [valid, info, ready]

    def status_database(self):
        info = {}
        valid = True
        ready = False

        if self.config.get('db_engine') == 'mysql':
            try:
                conn = MySQLdb.connect(
                    host=self.config.get('db_host'),
                    port=self.config.get('db_port'),
                    db=self.config.get('db_name'),
                    user=self.config.get('db_user'),
                    password=self.config.get('db_password'),
                    connect_timeout=5
                )
                conn.close()
                ready = True

            except (MySQLdb.Error, TypeError) as err:
                info = str(err)
                valid = False

            #except MySQLdb.Error as err:
            #    info = str(err)
            #    valid = False

        elif self.config.get('db_engine') == 'postgresql':
            try:
                conn = psycopg2.connect(
                    host=self.config.get('db_host'),
                    port=self.config.get('db_port'),
                    database=self.config.get('db_name'),
                    user=self.config.get('db_user'),
                    password=self.config.get('db_password'),
                    connect_timeout=5
                )
                conn.close()
                ready = True

            except (psycopg2.Error, TypeError) as err:
                info = str(err)
                valid = False
        else:
            valid = False
            info = 'Engine not supported'

        return [valid, info, ready]

    def status_rabbitmq(self):
        info = {}
        valid = False
        ready = False

        try:
            username = self.config.get('rabbitmq_admin_user')
            password = self.config.get('rabbitmq_admin_password')
            host = self.config.get('rabbitmq_host')
            credentials = pika.PlainCredentials(username, password)
            parameters = pika.ConnectionParameters(host, credentials=credentials)
            connection = pika.BlockingConnection(parameters)
            valid = True

            # todo: what test what can I do with rabbitmq to be ready?
            ready = True
        except (pika.exceptions.AMQPError, AttributeError, TypeError) as err:
            info = str(err)
            valid = False

        return [valid, info, ready]

    def status_redis(self):
        info = {}
        valid = False
        ready = False
        try:
            r = redis.Redis(host=self.config.get('redis_host'),
                            port=self.config.get('redis_port'),
                            password=self.config.get('redis_password'),
                            db=self.config.get('redis_database'))
            r.ping()

            r.set('test_tesla', 'testing_redis')
            if r.get('test_tesla').decode('utf8') == 'testing_redis':
                r.delete('test_tesla')
                ready = True

            r.close()
            valid = True
        except (redis.exceptions.ConnectionError, TypeError, redis.exceptions.ResponseError) as err:
            info = str(err)
            valid = False

        return [valid, info, ready]

    def status_minio(self):
        info = {}
        valid = False
        ready = False
        try:
            s3 = boto3.client('s3',
                              endpoint_url=self.config.get('STORAGE_URL'),
                              aws_access_key_id=self.config.get('STORAGE_ACCESS_KEY'),
                              aws_secret_access_key=self.config.get('STORAGE_SECRET_KEY'),
                              aws_session_token=None,
                              region_name=self.config.get('STORAGE_REGION'),
                              config=boto3.session.Config(signature_version='s3v4'),
                              #verify=self.config.get('STORAGE_SSL_VERIFY')
                              verify=False
                              )
            s3.list_buckets()
            valid = True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError, TypeError) as err:
            info = str(err)
            valid = False

        try:
            buckets = s3.list_buckets()
            if len(buckets.get('Buckets')) > 0:
                found_tesla_bucket = False
                found_tesla_public_bucket = False
                for bucket in buckets.get('Buckets'):
                    if bucket.get('Name') == self.config.get('STORAGE_BUCKET_NAME'):
                        found_tesla_bucket = True
                    elif bucket.get('Name') == self.config.get('STORAGE_PUBLIC_BUCKET_NAME'):
                        policy = {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Principal": {"AWS": ["*"]},
                                    "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                                    "Resource": ["arn:aws:s3:::{}".format(self.config.get('STORAGE_PUBLIC_BUCKET_NAME'))],
                                },
                                {
                                    "Effect": "Allow",
                                    "Principal": {"AWS": ["*"]},
                                    "Action": ["s3:GetObject"],
                                    "Resource":
                                        ["arn:aws:s3:::{}/*".format(self.config.get('STORAGE_PUBLIC_BUCKET_NAME'))]
                                },
                            ],
                        }

                        # s3.put_bucket_policy(Bucket=self.config.get('STORAGE_PUBLIC_BUCKET_NAME'), Policy=json.dumps(policy))
                        policy2 = s3.get_bucket_policy(Bucket=self.config.get('STORAGE_PUBLIC_BUCKET_NAME'))
                        if policy == json.loads(policy2.get('Policy')):
                            found_tesla_public_bucket = True

                if found_tesla_public_bucket is True and found_tesla_bucket is True:
                    ready = True

        except (botocore.exceptions.ClientError, TypeError, botocore.exceptions.NoCredentialsError) as err:
            info = str(err)

        return [valid, info, ready]

    def status(self) -> [bool, dict, bool]:
        valid = False
        info = {}
        ready = False

        if self.module == 'VAULT':
            [valid, info, ready] = self.status_vault()
        elif self.module == 'DATABASE':
            [valid, info, ready] = self.status_database()
        elif self.module == 'RABBITMQ':
            [valid, info, ready] = self.status_rabbitmq()
        elif self.module == 'REDIS':
            [valid, info, ready] = self.status_redis()
        elif self.module == 'MINIO':
            [valid, info, ready] = self.status_minio()

        return [valid, info, ready]

    def to_json(self):
        [valid, info, ready] = self.status()
        errors = {}
        return {
            'valid': valid,
            'info': info,
            'errors': errors,
            'ready': ready
        }


class CommandStatus:
    def __init__(self, command, status, info) -> None:
        super().__init__()
        self._command = command
        self._status = status
        self._info = info

    @property
    def command(self):
        return self._command

    @property
    def status(self):
        return self._status

    @property
    def info(self):
        return self._info

    def to_json(self):
        return {
            'command': self.command,
            'status': self.status,
            'info': self.info
        }
