from django import forms
from .base import ConfigForm

VAULT_BACKEND = [
    ('file', 'file'),
    ('database', 'database'),
]

TRUE_FALSE_CHOICES = [
    ('True', 'True'),
    ('False', 'False'),
]


class TeslaServiceVaultForm(ConfigForm):
    url = forms.CharField(label='Vault URL', max_length=255)
    ssl_verify = forms.ChoiceField(choices=TRUE_FALSE_CHOICES)
    token = forms.CharField(label='Vault token', max_length=512, required=False)
    keys = forms.CharField(label='Vault keys', max_length=512)
    backend = forms.ChoiceField(choices=VAULT_BACKEND)
    vault_db_host = forms.CharField(label='Database host', max_length=255, required=False)
    vault_db_port = forms.CharField(label='Database port', max_length=255, required=False)
    vault_db_name = forms.CharField(label='Database name', max_length=255, required=False)
    vault_db_user = forms.CharField(label='Database user', max_length=255, required=False)
    vault_db_password = forms.CharField(label='Database password', max_length=255,
                                  widget=forms.PasswordInput(render_value=True), required=False)
    mount_path_kv = forms.CharField(label='Mount path KV', max_length=255)
    mount_path_transit = forms.CharField(label='Mount path transit', max_length=255)
    mount_path_approle = forms.CharField(label='Mount path approle', max_length=255)
    policies_prefix = forms.CharField(label='Policies prefix', max_length=255)
    approle_default_ttl = forms.CharField(label='Approle default TTL', max_length=255)
    approle_max_ttl = forms.CharField(label='Approle max TTL', max_length=255)

    _field_correspondence = [
        ('url', 'VAULT_URL'),
        ('ssl_verify', 'VAULT_SSL_VERIFY'),
        ('token', 'VAULT_TOKEN'),
        ('keys', 'VAULT_KEYS'),
        ('backend', 'VAULT_BACKEND'),
        ('vault_db_host', 'VAULT_DB_HOST'),
        ('vault_db_port', 'VAULT_DB_PORT'),
        ('vault_db_name', 'VAULT_DB_NAME'),
        ('vault_db_user', 'VAULT_DB_USER'),
        ('vault_db_password', 'VAULT_DB_PASSWORD'),
        ('mount_path_kv', 'VAULT_MOUNT_PATH_KV'),
        ('mount_path_transit', 'VAULT_MOUNT_PATH_TRANSIT'),
        ('mount_path_approle', 'VAULT_MOUNT_PATH_APPROLE'),
        ('policies_prefix', 'VAULT_POLICIES_PREFIX'),
        ('approle_default_ttl', 'VAULT_APPROLE_DEFAULT_TTL'),
        ('approle_max_ttl', 'VAULT_APPROLE_MAX_TTL'),
    ]
