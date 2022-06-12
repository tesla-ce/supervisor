from django import forms
from .base import ConfigForm

AUTH_CHOICES = [
    ('none','None'),
    ('acl_token','ACL Token'),
    ('client_cert','Client Certificate'),
]


class NomadConsulForm(ConfigForm):
    nomad_addr = forms.CharField(label='Address', max_length=100)
    nomad_datacenters = forms.CharField(label='Datacenters', max_length=100)
    nomad_region = forms.CharField(label='Region', max_length=100)
    nomad_authOptions = forms.TypedChoiceField(choices=AUTH_CHOICES, widget=forms.RadioSelect, coerce=str, initial='none')
    nomad_acl_token = forms.CharField(label='Token', max_length=100, required=False)
    #nomad_skip_verify = forms.BooleanField(label='Skip TLS verification', initial=False, required=False)
    #nomad_tls_servername = forms.CharField(label='TLS server name', max_length=100, required=False),
    consul_addr = forms.CharField(label='Address', max_length=100)
    consul_authOptions = forms.TypedChoiceField(choices=AUTH_CHOICES, widget=forms.RadioSelect, coerce=str, initial='none')
    consul_acl_token = forms.CharField(label='Token', max_length=100, required=False)

    _field_correspondence = [
        ('nomad_addr', 'NOMAD_ADDR'),
        ('nomad_datacenters', 'NOMAD_DATACENTERS'),
        ('nomad_region', 'NOMAD_REGION'),
        #('nomad_skip_verify', 'NOMAD_SKIP_VERIFY'),
        #('nomad_tls_servername', 'NOMAD_TLS_SERVER_NAME'),
        ('nomad_authOptions', 'NOMAD_AUTH_TYPE'),
        ('nomad_acl_token', 'NOMAD_ACL_TOKEN'),
        ('consul_addr', 'CONSUL_ADDR'),
        #('consul_skip_verify', 'CONSUL_SKIP_VERIFY'),
        #('consul_tls_servername', 'CONSUL_TLS_SERVER_NAME'),
        ('consul_authOptions', 'CONSUL_AUTH_TYPE'),
        ('consul_acl_token', 'CONSUL_ACL_TOKEN'),
    ]

    def clean_nomad_authOptions(self):
        authOptions = self.cleaned_data['nomad_authOptions']
        if authOptions is None:
            authOptions = 'none'
        return authOptions

    def parse_config_value(self, field, value):
        if field == 'nomad_datacenters':
            if value is None:
                value = ''
            elif isinstance(value, list):
                value = ','.join(value)
        return value


class SwarmForm(ConfigForm):
    api_addr = forms.CharField(label='Address', max_length=100)

    _field_correspondence = []
