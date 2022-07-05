import base64
import binascii
from urllib.parse import urlparse
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
    # consul_skip_verify = forms.BooleanField(label='Skip TLS verification', initial=False, required=False)
    # consul_tls_servername = forms.CharField(label='TLS server name', max_length=100, required=False),

    _field_correspondence = [
        ('nomad_addr', 'NOMAD_ADDR'),
        ('nomad_datacenters', 'NOMAD_DATACENTERS'),
        ('nomad_region', 'NOMAD_REGION'),
        #('nomad_skip_verify', 'NOMAD_SKIP_VERIFY'),
        #('nomad_tls_servername', 'NOMAD_TLS_SERVER_NAME'),
        ('nomad_authOptions', 'NOMAD_AUTH_TYPE'),
        ('nomad_acl_token', 'NOMAD_ACL_TOKEN'),
        ('consul_host', 'CONSUL_HOST'),
        ('consul_port', 'CONSUL_PORT'),
        ('consul_scheme', 'CONSUL_SCHEME'),
        #('consul_skip_verify', 'CONSUL_SKIP_VERIFY'),
        #('consul_tls_servername', 'CONSUL_TLS_SERVER_NAME'),
        ('consul_authOptions', 'CONSUL_AUTH_TYPE'),
        ('consul_acl_token', 'CONSUL_ACL_TOKEN'),
    ]

    def load_config(self, config):
        super().load_config(config)
        self.fields['consul_addr'].initial = '{}://{}:{}'.format(
            config.get('CONSUL_SCHEME'),
            config.get('CONSUL_HOST'),
            config.get('CONSUL_PORT'),
        )

    def clean_nomad_authOptions(self):
        authOptions = self.cleaned_data['nomad_authOptions']
        if authOptions is None:
            authOptions = 'none'
        return authOptions

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['consul_addr'] is not None:
            parsed_consul = urlparse(cleaned_data['consul_addr'])
            cleaned_data['consul_scheme'] = parsed_consul.scheme
            cleaned_data['consul_host'] = parsed_consul.hostname
            if parsed_consul.port is None:
                if parsed_consul.scheme == 'http':
                    cleaned_data['consul_port'] = 80
                else:
                    cleaned_data['consul_port'] = 443
            else:
                cleaned_data['consul_port'] = parsed_consul.port

        return cleaned_data

    def parse_config_value(self, field, value):
        if field == 'nomad_datacenters':
            if value is None:
                value = ''
            elif isinstance(value, list):
                value = ','.join(value)
        return value


class SwarmForm(ConfigForm):
    swarm_service_prefix = forms.CharField(label='Service prefix', max_length=512)
    swarm_base_url = forms.CharField(label='Base url', max_length=512)

    swarm_client_key = forms.CharField(widget=forms.Textarea(attrs={'name':'Client key', 'rows':3, 'cols':5}), required=False)
    swarm_client_cert = forms.CharField(widget=forms.Textarea(attrs={'name':'Client cert', 'rows':3, 'cols':5}), required=False)
    swarm_specific_ca_cert = forms.CharField(widget=forms.Textarea(attrs={'name':'Specific CA certificate', 'rows':3, 'cols':5}), required=False)

    _field_correspondence = [
        ('swarm_service_prefix', 'SWARM_SERVICE_PREFIX'),
        ('swarm_base_url', 'SWARM_BASE_URL'),
        ('swarm_client_key', 'SWARM_CLIENT_KEY'),
        ('swarm_client_cert', 'SWARM_CLIENT_CERT'),
        ('swarm_specific_ca_cert', 'SWARM_SPECIFIC_CA_CERT'),
    ]

    def update_config(self, config):
        for field in self._field_correspondence:
            if (field[0] == 'swarm_client_key' or field[0] == 'swarm_client_cert' or field[0] == 'swarm_specific_ca_cert') and self.data.get(field[0]) != '':
                try:
                    b64value = base64.b64encode(self.data.get(field[0]).encode('utf8'))
                    config.set(field[1], b64value.decode('utf8'))
                except (TypeError, binascii.Error) as err:
                    pass
            else:
                config.set(field[1], self.data.get(field[0]))

    def load_config(self, config):
        for field in self._field_correspondence:
            if (field[0] == 'swarm_client_key' or field[0] == 'swarm_client_cert' or field[0] == 'swarm_specific_ca_cert') and self.parse_config_value(field[0], config.get(field[1])) != '':
                try:
                    if self.parse_config_value(field[0], config.get(field[1])) is not None:
                        self.fields[field[0]].initial = base64.b64decode(self.parse_config_value(field[0], config.get(field[1])).encode('utf8')).decode('utf8')
                except (TypeError, binascii.Error) as err:
                    pass

            else:
                self.fields[field[0]].initial = self.parse_config_value(field[0], config.get(field[1]))
