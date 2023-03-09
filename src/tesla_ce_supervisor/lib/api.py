import uuid

from django.conf import settings
import requests
from .exceptions import ProviderExistsException, VLEExistsException


class TeSLAAPI:

    def __init__(self, config):
        self.config = config
        self.verify_ssl = True
        self.domain = self.config.get('tesla_domain')
        self.access_token = None
        self.headers = {}
        self.profile = {}

        if settings.DEBUG is True:
            self.verify_ssl = False

    def login(self, inst_user=False):
        user = self.config.get('tesla_admin_mail')

        if inst_user is True:
            user = "inst_{}".format(self.config.get('tesla_admin_mail'))

        password = self.config.get('tesla_admin_password')
        url = "https://{}/api/v2/auth/login".format(self.domain)

        data = {
            'email': user,
            'password': password
        }

        response = requests.post(url, data, verify=self.verify_ssl)
        self.access_token = response.json()
        self.headers = {"Authorization": "JWT {}".format(self.access_token.get('token').get('access_token'))}

    @staticmethod
    def get_selected_instrument_acronym(module):
        instruments_acronym = {"TFR": "fr", "TPT": "plag", "TKS": "ks", "TFA": "fa", "TVR": "vr"}
        return instruments_acronym.get(module.upper())

    def get_provider(self, module):
        selected_instrument_acronym = self.get_selected_instrument_acronym(module)
        self.login()

        # check if provider is registered
        url = "https://{}/api/v2/admin/instrument/".format(self.domain)
        response = requests.get(url, {}, verify=self.verify_ssl, headers=self.headers)
        aux = response.json()
        instruments = aux.get('results')

        for instrument in instruments:
            if selected_instrument_acronym == instrument.get('acronym'):
                instrument_id = instrument.get('id')

                url = 'https://{}/api/v2/admin/instrument/{}/provider/'.format(self.domain, instrument_id)
                response = requests.get(url, verify=self.verify_ssl, headers=self.headers)
                aux = response.json()
                providers = aux.get('results')

                if providers:
                    for prov in providers:
                        if prov.get('acronym') == module.lower():
                            return [prov, instrument_id]

                return [None, instrument_id]

    def register_provider(self, module):
        self.login()
        selected_instrument_acronym = self.get_selected_instrument_acronym(module)
        [prov, instrument_id] = self.get_provider(module)

        if prov:
            #url = 'https://{}/api/v2/admin/instrument/{}/provider/{}/'.format(self.domain, instrument_id, prov.get('id'))
            #response = requests.delete(url, verify=self.verify_ssl, headers=self.headers)

            raise ProviderExistsException(provider_id=prov.get('id'))

        # provider not exists
        # download json of instrument
        if selected_instrument_acronym == 'plag':
            selected_instrument_acronym = 'pt'
        options = 'options'
        if module.lower() == 'tfr':
            options = 'fr_tfr.info'
        response = requests.get('https://raw.githubusercontent.com/tesla-ce/provider-{}-{}/main/{}.json'.
                                format(selected_instrument_acronym, module.lower(), options), headers=self.headers,
                                verify=self.verify_ssl)

        provider_json = response.json()
        # Register provider
        provider_json['enabled'] = True
        provider_json['validation_active'] = True

        if 'instrument' in provider_json:
            del provider_json['instrument']

        url = 'https://{}/api/v2/admin/instrument/{}/provider/'.format(self.domain, instrument_id)

        response_provider = requests.post(url, json=provider_json, headers=self.headers, verify=self.verify_ssl)
        provider_register = response_provider.json()

        # enable instrument
        url = 'https://{}/api/v2/admin/instrument/{}/'.format(self.domain, instrument_id)
        requests.patch(url, json={'enabled': True}, headers=self.headers, verify=self.verify_ssl)

        return provider_register.get('credentials')

    def get_profile(self):
        self.login()
        url = 'https://{}/api/v2/auth/profile'.format(self.domain)
        response = requests.get(url, headers=self.headers, verify=self.verify_ssl)
        self.profile = response.json()

    def create_inst_admin(self, institution_id):
        # enable global admin to default institution

        url = 'https://{}/api/v2/admin/user/'.format(self.domain)

        response = requests.get(url, headers=self.headers, verify=self.verify_ssl)
        users = response.json()

        user_id = None
        if users.get('results') is not None:
            for user in users.get('results'):
                if user.get('username') == "inst_{}".format(self.profile['username']):
                    user_id = user.get('id')

        data = {
            'username': "inst_{}".format(self.profile['username']),
            'uid': self.profile['username'],
            'email': "inst_{}".format(self.profile['username']),
            'first_name': self.profile['username'],
            'last_name': self.profile['username'],
            'login_allowed': True,
            'is_active': True,
            'is_staff': True,
            'institution_id': institution_id,
            'password': self.config.get('tesla_admin_password'),
            'password2': self.config.get('tesla_admin_password'),
            'inst_admin': True,
            'legal_admin': True,
            'send_admin': True,
            'data_admin': True
        }

        if user_id is None:
            response = requests.post(url, json=data, headers=self.headers, verify=self.verify_ssl)
        else:
            url = url = 'https://{}/api/v2/admin/user/{}/'.format(self.domain, user_id)
            response = requests.patch(url, json=data, headers=self.headers, verify=self.verify_ssl)

    def get_vle(self, module, institution_id=None):
        if institution_id is None:
            self.login()
            institution_id = self.profile['institutions'][0]['id']

        url = 'https://{}/api/v2/institution/{}/vle/'.format(self.domain, institution_id)
        response = requests.get(url, headers=self.headers, verify=self.verify_ssl)
        vles = response.json()
        if vles.get('results'):
            for vle in vles.get('results'):
                if vle.get('name') == "default_{}".format(module):
                    return vle
        return None

    def register_vle(self, module):
        # Get the user profile
        self.get_profile()

        institution_id = self.profile['institutions'][0]['id']
        # Enable direct registration from VLE
        url = 'https://{}/api/v2/admin/institution/{}/'.format(self.domain, institution_id)

        data = {
            'disable_vle_user_creation': False,
            'disable_vle_learner_creation': False,
            'disable_vle_instructor_creation': False,
            'allow_learner_report': True,
            'allow_learner_audit': True,
            'allow_valid_audit': True,
            'allowed_domains': "{}.{}".format(module, self.domain)
        }
        response = requests.patch(url, json=data, headers=self.headers, verify=self.verify_ssl)

        # Create or update inst admin
        self.create_inst_admin(institution_id)
        self.login(inst_user=True)

        # get VLE
        vle = self.get_vle(module, institution_id)

        if vle is not None:
            raise VLEExistsException(vle_id=vle.get('id'))
        # Register a VLE
        vle_data = {
            'type': 0,  # 0 is the code for Moodle
            'name': "default_{}".format(module),
            'url': '{}.{}'.format(module, self.domain),
            'client_id': str(uuid.uuid4())
        }
        # institution_id = profile['institution']['id']

        url = 'https://{}/api/v2/institution/{}/vle/'.format(self.domain, institution_id)
        response = requests.post(url, json=vle_data, headers=self.headers, verify=self.verify_ssl)
        vle_data = response.json()
        return vle_data.get('credentials')


