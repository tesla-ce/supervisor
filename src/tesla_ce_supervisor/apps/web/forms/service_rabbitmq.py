from django import forms
from .base import ConfigForm

CELERY_PROTOCOL = [
    ('amqp', 'amqp'),
    ('sqs', 'sqs'),
]


class TeslaServiceRabbitMqForm(ConfigForm):
    rabbitmq_erlang_cookie = forms.CharField(label='Erlang cookie', max_length=255)
    rabbitmq_admin_user = forms.CharField(label='Admin user', max_length=255)
    rabbitmq_admin_password = forms.CharField(label='Admin password', max_length=255, widget=forms.PasswordInput(render_value=True))
    rabbitmq_admin_port = forms.CharField(label='Admin port', max_length=255)
    rabbitmq_port = forms.CharField(label='Port', max_length=255)
    rabbitmq_host = forms.CharField(label='Host', max_length=255)

    rabbitmq_broker_protocol = forms.ChoiceField(choices=CELERY_PROTOCOL)
    rabbitmq_broker_user = forms.CharField(label='Broker user', max_length=255)
    rabbitmq_broker_password = forms.CharField(label='Broker password', max_length=255, widget=forms.PasswordInput(render_value=True))
    rabbitmq_broker_host = forms.CharField(label='Broker host', max_length=255)
    rabbitmq_broker_region = forms.CharField(label='Broker region', max_length=255)
    rabbitmq_broker_port = forms.CharField(label='Broker port', max_length=255)
    rabbitmq_broker_vhost = forms.CharField(label='Broker vhost', max_length=255)
    rabbitmq_queue_enrolment = forms.CharField(label='Queue enrolment', max_length=255)
    rabbitmq_queue_enrolment_storage = forms.CharField(label='Queue enrolment storage', max_length=255)
    rabbitmq_queue_enrolment_validation = forms.CharField(label='Queue enrolment validation', max_length=255)
    rabbitmq_queue_verification = forms.CharField(label='Queue verification', max_length=255)
    rabbitmq_queue_alerts = forms.CharField(label='Queue alerts', max_length=255)
    rabbitmq_queue_reporting = forms.CharField(label='Queue reporting', max_length=255)
    rabbitmq_queues = forms.CharField(label='Queues', max_length=255, required=False)

    _field_correspondence = [
        ('rabbitmq_erlang_cookie', 'RABBITMQ_ERLANG_COOKIE'),
        ('rabbitmq_admin_user', 'RABBITMQ_ADMIN_USER'),
        ('rabbitmq_admin_password', 'RABBITMQ_ADMIN_PASSWORD'),
        ('rabbitmq_admin_port', 'RABBITMQ_ADMIN_PORT'),
        ('rabbitmq_port', 'RABBITMQ_PORT'),
        ('rabbitmq_host', 'RABBITMQ_HOST'),
        ('rabbitmq_broker_protocol', 'CELERY_BROKER_PROTOCOL'),
        ('rabbitmq_broker_user', 'CELERY_BROKER_USER'),
        ('rabbitmq_broker_password', 'CELERY_BROKER_PASSWORD'),
        ('rabbitmq_broker_host', 'CELERY_BROKER_HOST'),
        ('rabbitmq_broker_region', 'CELERY_BROKER_REGION'),
        ('rabbitmq_broker_port', 'CELERY_BROKER_PORT'),
        ('rabbitmq_broker_vhost', 'CELERY_BROKER_VHOST'),
        ('rabbitmq_queue_enrolment', 'CELERY_QUEUE_ENROLMENT'),
        ('rabbitmq_queue_enrolment_storage', 'CELERY_QUEUE_ENROLMENT_STORAGE'),
        ('rabbitmq_queue_enrolment_validation', 'CELERY_QUEUE_ENROLMENT_VALIDATION'),
        ('rabbitmq_queue_verification', 'CELERY_QUEUE_VERIFICATION'),
        ('rabbitmq_queue_alerts', 'CELERY_QUEUE_ALERTS'),
        ('rabbitmq_queue_reporting', 'CELERY_QUEUE_REPORTING'),
        ('rabbitmq_queues', 'CELERY_QUEUES'),
    ]
