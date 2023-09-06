from django import forms
from .base import ConfigForm

ENGINE_CHOICES = [
    ('mysql', 'MySQL'),
    ('postgresql', 'Postgres SQL'),
]


class TeslaServiceDatabaseForm(ConfigForm):
    database_host = forms.CharField(label='Host', max_length=255)
    database_port = forms.CharField(label='Port', max_length=255)
    database_engine = forms.ChoiceField(choices=ENGINE_CHOICES)
    database_db_name = forms.CharField(label='Database name', max_length=255)
    database_db_user = forms.CharField(label='Database user', max_length=255)
    database_db_password = forms.CharField(label='Database password', max_length=255, widget=forms.PasswordInput(render_value=True))
    database_db_root_password = forms.CharField(label='Database root password', max_length=255, widget=forms.PasswordInput(render_value=True))

    _field_correspondence = [
        ('database_host', 'DB_HOST'),
        ('database_port', 'DB_PORT'),
        ('database_engine', 'DB_ENGINE'),
        ('database_db_name', 'DB_NAME'),
        ('database_db_user', 'DB_USER'),
        ('database_db_password', 'DB_PASSWORD'),
        ('database_db_root_password', 'DB_ROOT_PASSWORD'),
    ]
