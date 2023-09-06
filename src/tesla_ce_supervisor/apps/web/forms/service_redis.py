from django import forms
from .base import ConfigForm


class TeslaServiceRedisForm(ConfigForm):
    redis_host = forms.CharField(label='Host', max_length=255)
    redis_port = forms.CharField(label='Port', max_length=255)
    redis_password = forms.CharField(label='Password', max_length=255, widget=forms.PasswordInput(render_value=True))
    redis_database = forms.CharField(label='Database', max_length=255)

    _field_correspondence = [
        ('redis_host', 'REDIS_HOST'),
        ('redis_port', 'REDIS_PORT'),
        ('redis_password', 'REDIS_PASSWORD'),
        ('redis_database', 'REDIS_DATABASE'),
    ]
