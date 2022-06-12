import os
from django.shortcuts import render, redirect

from tesla_ce_supervisor.lib.tesla import TeslaClient
from tesla_ce_supervisor.lib.utils import to_list, to_tuple, utils_get_config


def step1(request):
    config = utils_get_config()

    if request.method =='POST':
        for key, item in request.POST.items():
            key = key.replace('__', '_')
            key = str(key).upper()
            if config.is_valid_key(key):
                config.set(key, item)

        client = TeslaClient()
        with open(os.path.join(client.get_config_path()), 'w') as config_file:
            config.write(config_file)

        return redirect('setup_step2')

    step = 0

    general_sections = (
        ('tesla', 'Generic configuration', (
            ('domain', 'Base domain', 'str', None, None, True),
            ('admin_mail', 'Mail of the administrator', 'str', None, None, True),
            ('institution_name', 'Name of the institution', 'str', 'Default Institution', None, True),
            ('institution_acronym', 'Acronym of the institution', 'str', 'default', None, True),
        )),
        ('deployment', 'Deployment configuration', (
            ('catalog_system', 'Catalog system', 'enum', 'swarm', ['consult', 'swarm'], True),
            ('orchestrator', 'Deploy system', 'enum', 'swarm', ['swarm', 'terraform+normad'], True),
            ('services', 'Deploy external services', 'bool', True, None, True),
            ('lb', 'Load balancer', 'enum', 'traefik', ['traefik', 'other'], True),
            ('data_path', 'Folder where volumes will be persisted', 'str', '/var/tesla', None, True),
            ('specialized_workers', 'If enabled, specialized workers will be deployed.', 'bool', True, True),
        )),
    )

    general_sections_list = to_list(general_sections)

    idx_section = 0
    for section in general_sections_list:
        for subsection in section[2]:
            key = "{}_{}".format(section[0], subsection[0])
            value = section[2][1][3]
            subsection[3] = config.get(key, value)

    general_sections = to_tuple(general_sections_list)

    # todo: add checkbox deploy load balancer?
    # todo: supervisor service privileged mode: yes/no

    return render(request, 'step1.html', {'config': config, 'sections': general_sections})


def step2(request):
    config = utils_get_config()

    if request.method =='POST':
        for key, item in request.POST.items():
            key = key.replace('__', '_')
            key = str(key).upper()
            if config.is_valid_key(key):
                config.set(key, item)

        client = TeslaClient()
        with open(os.path.join(client.get_config_path()), 'w') as config_file:
            config.write(config_file)

        return redirect('setup_step3')

    service_sections = (
        ('db', 'Database configuration', (
            ('host', 'Database host', 'str', 'localhost', None, True),
            ('engine', 'Database engine', 'enum', 'mysql', ['mysql', 'postgresql',], True),
            ('port', 'Database port', 'int', 3306, None, True),
            ('name', 'Database name', 'str', 'tesla', None, True),
            ('user', 'Database user', 'str', None, None, True),
            ('password', 'Database password', 'str', None, None, True),
            ('root_user', 'Database root username', 'str', 'root', None, True),
            ('root_password', 'Database root password', 'str', None, None, True),
        )),
        ('vault', 'HashiCorp Vault configuration', (
            ('url', 'Vault complete URL', 'str', 'http://localhost:8200', None, True),
            ('ssl_verify', 'Verify SSL', 'bool', True, None, True),
            ('token', 'Token to authenticate', 'str', None, None, True),
            ('role_id', 'Role ID value to authenticate', 'list', None, None, False),
            ('secret_id', 'Secret ID value to authenticate', 'list', None, None, False),
            ('keys', 'Unseal keys for Vault', 'list', None, None, True),
            ('management', 'Allow Vault management', 'bool', False, None, False),
            ('mount_path_kv', 'Mount path for KV secrets engine', 'str', 'tesla-ce/kv', None, True),
            ('mount_path_transit', 'Mount path for transit encryption engine', 'str', 'tesla-ce/transit', None, True),
            ('mount_path_approle', 'Mount path for approle auth engine', 'str', 'tesla-ce/approle', None, True),
            ('policies_prefix', 'Prefix prepended to ACL policy names', 'str', 'tesla-ce/policy/', None, True),
            ('backend', 'Vault backend', 'enum', 'file', ['file', 'database', ], True, 'filter_field'),
            ('db_host', 'MySQL host for vault database', 'str', None, None, True, 'vault__backend', 'database'),
            ('db_port', 'MySQL port for vault database', 'int', 3306, None, True, 'vault__backend', 'database'),
            ('db_name', 'MySQL database name for vault database', 'str', None, None, True, 'vault__backend', 'database'),
            ('db_user', 'MySQL user for vault database', 'str', None, None, True, 'vault__backend', 'database'),
            ('db_password', 'MySQL password for vault database', 'str', None, None, True, 'vault__backend', 'database'),

        )),
        ('redis', 'Redis configuration', (
            ('host', 'Redis host', 'str', 'localhost', None, True),
            ('port', 'Redis port', 'int', 6379, None, True),
            ('password', 'Redis password', 'str', None, None, True),
            ('database', 'Redis database', 'int', 1, None, True),
        )),
        ('storage', 'Storage configuration (S3 or Minio)', (
            ('url', 'Storage url', 'str', 'http://localhost:9000', None, True),
            ('bucket_name', 'Storage default private bucket', 'str', 'tesla', None, True),
            ('public_bucket_name', 'Storage default public bucket', 'str', 'tesla-public', None, True),
            ('region', 'Storage region', 'str', 'eu-west-1', None, True),
            ('access_key', 'Storage access key id', 'str', None, None, True),
            ('secret_key', 'Storage secret access key', 'str', None, None, True),
            ('ssl_verify', 'Verify SSL', 'bool', True, None, True),
        )),
        ('celery', 'Celery configuration (RabbitMQ or SQS)', (
            ('broker_protocol', 'Protocol to communicate with brocker', 'enum', 'amqp', ['amqp', 'sqs'], True),
            ('broker_user', 'User to authenticate with RabbitMQ or KEY for Amazon SQS', 'str', None, True),
            ('broker_password', 'Password to authenticate with RabbitMQ or SECRET for Amazon SQS', 'str', None, True),
            ('broker_host', 'Host for RabbitMQ', 'str', 'localhost', True),
            ('broker_region', 'Region for Amazon SQS', 'str', 'eu-west-1', True),
            ('broker_port', 'Port for RabbitMQ', 'int', 5672, True),
            ('broker_vhost', 'RabbitMQ Virtual Host', 'str', '/', True),
            ('queue_default', 'Name of the default queue used for periodic tasks', 'str', 'tesla', True),
            ('queue_enrolment', 'Name of the default queue for enrolment', 'str', 'tesla_enrolment', True),
            ('queue_enrolment_storage', 'Name of the storage queue for enrolment', 'str',
             'tesla_enrolment_storage', True),
            ('queue_enrolment_validation', 'Name of the validation queue for enrolment', 'str',
             'tesla_enrolment_validate', True),
            ('queue_verification', 'Name of the default queue for verification', 'str', 'tesla_verification', True),
            ('queue_alerts', 'Name of the default queue for alerts', 'str', 'tesla_alerts', True),
            ('queue_reporting', 'Name of the default queue for reports', 'str', 'tesla_reporting', True),
            ('queues', 'List of queues a worker will listen to.', 'list', None, False),
        )),
        ('django', 'DJango configuration', (
            ('secret_key', 'DJango secret value', 'str', None, None, True),
            ('allowed_hosts', 'Allowed hosts', 'list', [], None, True),
        ))
    )

    service_sections_list = to_list(service_sections)

    idx_section = 0
    for section in service_sections_list:
        for subsection in section[2]:
            key = "{}_{}".format(section[0], subsection[0])
            value = section[2][1][3]
            subsection[3] = config.get(key, value)

    service_sections = to_tuple(service_sections_list)

    return render(request, 'step2.html', {'config': config, 'service_sections': service_sections, 'step': 2})

def step3(request):
    config = utils_get_config()

    if request.method =='POST':  # comes here when you are making a post request via submitting the form
        # Register user
        return redirect('/')

    step = 0
    services = [
        {
            "name": "database",
            "status": "success",
            "error_message": ""
        },
        {
            "name": "redis",
            "status": "danger",
            "error_message": "Lorem ipsum redis"
        },
        {
            "name": "rabbitmq",
            "status": "danger",
            "error_message": "Lorem ipsum"
        },
        {
            "name": "storage",
            "status": "danger",
            "error_message": "Lorem ipsum"
        },
        {
            "name": "vault",
            "status": "danger",
            "error_message": "Lorem ipsum vault"
        },
    ]

    tesla_supervisor = [
        {
            "name": "supervisor",
            "status": "success",
            "error_message": ""
        },
    ]

    tesla_core = [

        {
            "name": "api",
            "status": "success",
            "error_message": ""
        },
        {
            "name": "workers",
            "status": "danger",
            "error_message": "Lorem ipsum workers"
        },
        {
            "name": "lapi",
            "status": "success",
            "error_message": ""
        },
        {
            "name": "dashboard",
            "status": "success",
            "error_message": ""
        }
    ]

    return render(request, 'step3.html', { "services": services, "tesla_core": tesla_core })
