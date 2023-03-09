from django import forms
from .base import ConfigForm


class TeslaMoodleForm(ConfigForm):
    db_host = forms.CharField(label='Database host', max_length=256)
    db_name = forms.CharField(label='Database name', max_length=256)
    db_user = forms.CharField(label='Database user', max_length=256)
    db_password = forms.CharField(label='Database password', max_length=256, widget=forms.PasswordInput(
        render_value=True))
    db_prefix = forms.CharField(label='Database prefix', max_length=100)
    cron_internal = forms.IntegerField(label='Cron interval')
    full_name = forms.CharField(label='Full name', max_length=100)
    short_name = forms.CharField(label='Short name', max_length=100)
    summary = forms.CharField(label='Summary', max_length=100)
    admin_user = forms.CharField(label='Admin user', max_length=100)
    admin_password = forms.CharField(label='Admin password', max_length=100)
    admin_email = forms.CharField(label='Admin email', max_length=100)

    _field_correspondence = [
        ('db_host', 'MOODLE_DB_HOST'),
        ('db_name', 'MOODLE_DB_NAME'),
        ('db_user', 'MOODLE_DB_USER'),
        ('db_password', 'MOODLE_DB_PASSWORD'),
        ('db_prefix', 'MOODLE_DB_PREFIX'),
        ('cron_internal', 'MOODLE_CRON_INTERVAL'),
        ('full_name', 'MOODLE_FULL_NAME'),
        ('short_name', 'MOODLE_SHORT_NAME'),
        ('summary', 'MOODLE_SUMMARY'),
        ('admin_user', 'MOODLE_ADMIN_USER'),
        ('admin_password', 'MOODLE_ADMIN_PASSWORD'),
        ('admin_email', 'MOODLE_ADMIN_EMAIL'),
    ]
