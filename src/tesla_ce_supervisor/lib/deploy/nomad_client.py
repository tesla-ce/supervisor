import os
import typing
import nomad
from urllib.parse import urlparse
from django.template.loader import render_to_string
from .base import BaseDeploy
from .exceptions import TeslaDeployNomadTemplateException, TeslaDeployNomadException
from ..tesla.conf import Config
from ..setup_options import SetupOptions


class NomadConfig:
    """
        Nomad configuration
    """
    # Nomad server URL
    nomad_url: str = 'http://127.0.0.1'

    # Nomad server port
    nomad_port: int = 4646

    # Nomad region
    nomad_region: str = 'global'

    # Nomad datacenters
    nomad_datacenters: typing.List[str] = []

    # Authentication
    nomad_auth: typing.Optional[typing.Union[typing.Literal["ACL"], typing.Literal["CERT"]]] = None

    # Nomad SecretID of an ACL token for authentication
    nomad_token: typing.Optional[str] = None

    # Path to a PEM encoded client certificate for TLS authentication
    nomad_client_cert: typing.Optional[str] = None

    # Path to an unencrypted PEM encoded private key matching the client certificate for TLS authentication
    nomad_client_key: typing.Optional[str] = None

    # Path to a PEM encoded CA cert file to use to verify the Nomad server SSL certificate.
    nomad_cacert: typing.Optional[str] = None

    # Path to a directory of PEM encoded CA cert files to verify the Nomad server SSL certificate.
    nomad_capath: typing.Optional[str] = None

    # Do not verify TLS certificate. This is highly not recommended.
    nomad_skip_verify: typing.Optional[bool] = False

    # The server name to use as the SNI host when connecting via TLS.
    nomad_tls_server_name: typing.Optional[str] = None

    def __init__(self, config, nomad_addr: typing.Optional[str] = None,
                 nomad_region: typing.Optional[str] = None,
                 nomad_datacenters: typing.Optional[typing.List[str]] = None,
                 nomad_auth: typing.Optional[typing.Union[typing.Literal["ACL"], typing.Literal["CERT"]]] = None,
                 nomad_token: typing.Optional[str] = None,
                 nomad_client_cert: typing.Optional[str] = None,
                 nomad_client_key: typing.Optional[str] = None,
                 nomad_cacert: typing.Optional[str] = None,
                 nomad_capath: typing.Optional[str] = None,
                 nomad_skip_verify: typing.Optional[bool] = False,
                 nomad_tls_server_name: typing.Optional[str] = None,
                 ) -> None:

        # Nomad configuration
        self.nomad_datacenters = self._set_value(
            config, nomad_datacenters, 'NOMAD_DATACENTERS', 'NOMAD_DATACENTERS', []
        )
        self.nomad_auth = self._set_value(
            config, nomad_auth
        )
        nomad_addr = self._set_value(config, nomad_addr, 'NOMAD_ADDR', 'NOMAD_ADDR')
        if nomad_addr is not None:
            parsed = urlparse(nomad_addr)
            self.nomad_url = ''
            if parsed.scheme is not None and len(parsed.scheme) > 0:
                self.nomad_url += '{}://'.format(parsed.scheme)
            self.nomad_url += '{}'.format(parsed.hostname)
            self.nomad_port = parsed.port
        self.nomad_region = self._set_value(config, nomad_region, 'NOMAD_REGION', 'NOMAD_REGION')

        # Verification
        self.nomad_skip_verify = self._set_value(
            config, nomad_skip_verify, 'NOMAD_SKIP_VERIFY', 'NOMAD_SKIP_VERIFY'
        )
        self.nomad_tls_server_name = self._set_value(
            config, nomad_tls_server_name, 'NOMAD_TLS_SERVER_NAME', 'NOMAD_TLS_SERVER_NAME'
        )
        self.nomad_cacert = os.getenv('NOMAD_CACERT', nomad_cacert)
        self.nomad_capath = os.getenv('NOMAD_CAPATH', nomad_capath)

        # Authentication configuration
        if self.nomad_auth == "ACL":
            self.nomad_token = self._set_value(nomad_token, 'NOMAD_TOKEN', 'NOMAD_TOKEN')
        elif self.nomad_auth == "CERT":
            self.nomad_token = self._set_value(nomad_client_cert, 'NOMAD_CLIENT_CERT', 'NOMAD_CLIENT_CERT')
            self.nomad_token = self._set_value(nomad_client_key, 'NOMAD_CLIENT_KEY', 'NOMAD_CLIENT_KEY')

    @staticmethod
    def _set_value(config, parameter, env_key=None, conf_key=None, default=None):
        if parameter is not None:
            return parameter
        default_value = None
        if conf_key is not None:
            default_value = config.get(conf_key)
        if env_key is not None:
            ret_val = os.getenv(env_key, default_value)
        else:
            ret_val = default_value
        if ret_val is None:
            ret_val = default
        return ret_val


class NomadDeploy(BaseDeploy):
    """
        Utility class for Nomad deployment
    """
    # Nomad configuration
    nomad_conf: typing.Optional[NomadConfig] = None

    def __init__(self, config: typing.Optional[Config] = None, nomad_conf: typing.Optional[NomadConfig] = None) -> None:
        super().__init__(config)
        self.nomad_conf = nomad_conf
        if self.nomad_conf is None:
            self.nomad_conf = NomadConfig(config)
        if self.nomad_conf.nomad_auth is None:
            self._client = nomad.Nomad(
                host=self.nomad_conf.nomad_url,
                port=self.nomad_conf.nomad_port,
                verify=self.nomad_conf.nomad_skip_verify
            )
        elif self.nomad_conf.nomad_auth == "ACL":
            self._client = nomad.Nomad(
                host=self.nomad_conf.nomad_url,
                port=self.nomad_conf.nomad_port,
                token=self.nomad_conf.nomad_token,
                verify=self.nomad_conf.nomad_skip_verify
            )
        elif self.nomad_conf.nomad_auth == "CERT":
            self._client = nomad.Nomad(
                host=self.nomad_conf.nomad_url,
                port=self.nomad_conf.nomad_port,
                cert=(self.nomad_conf.nomad_client_cert,self.nomad_conf.nomad_client_key),
                verify=self.nomad_conf.nomad_skip_verify
            )

    def write_scripts(self) -> None:
        """
            Write deployment scripts
        """
        pass

    def deploy_lb(self) -> dict:
        """
            Deploy Load Balancer
        """

        context = {
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'traefik_image': 'traefik:v2.5',
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            #'consul_address': '',
            #'consul_scheme': '',
            'TESLA_ADMIN_MAIL': self._config.get('TESLA_ADMIN_MAIL')
        }

        task_def = self._remove_empty_lines(render_to_string('lb/traefik/nomad/traefik.nomad', context))

        try:
            job_def = self._client.jobs.parse(task_def)
        except nomad.api.exceptions.BadRequestNomadException as err:
            raise TeslaDeployNomadTemplateException(err.nomad_resp.reason)

        try:
            response = self._client.job.register_job("traefik", {'Job': job_def})
        except nomad.api.exceptions.BadRequestNomadException as err:
            raise TeslaDeployNomadException(err.nomad_resp.reason)

        return response

    def remove_lb(self) -> dict:
        """
            Remove deployed Load Balancer
        """
        response = self._client.job.deregister_job('traefik', True)
        return response

    def get_lb_script(self) -> SetupOptions:
        """
            Get the script to deploy Load Balancer
        """
        context = {
            'count': 1,
            'nomad_datacenters': str(self.nomad_conf.nomad_datacenters).replace("'", '"'),
            'nomad_region': self.nomad_conf.nomad_region,
            'traefik_image': 'traefik:v2.5',
            'DEPLOYMENT_DATA_PATH': self._config.get('DEPLOYMENT_DATA_PATH'),
            #'consul_address': '',
            #'consul_scheme': '',
            'TESLA_ADMIN_MAIL': self._config.get('TESLA_ADMIN_MAIL')
        }

        task_def = self._remove_empty_lines(render_to_string('lb/traefik/nomad/traefik.nomad', context))

        script = SetupOptions()
        script.add_command(
            command='nomad job run tesla-ce-lb-traefik.nomad',
            description='Create new Nomad job for Traefik Load Balancer'
        )
        script.add_file(
            filename='tesla-ce-lb-traefik.nomad',
            description='Job description for Traefik Load Balancer',
            content=task_def,
            mimetype='application/hcl'
        )

        return script

    def deploy_vault(self) -> dict:
        """
            Deploy Hashicorp Vault
        """
        return {}

    def get_vault_script(self) -> SetupOptions:
        """
            Get the script to deploy Hashicorp Vault
        """
        script = SetupOptions()
        return script

    def deploy_minio(self) -> dict:
        """
            Deploy MinIO
        """
        return {}

    def get_minio_script(self) -> SetupOptions:
        """
            Get the script to deploy MinIO
        """
        script = SetupOptions()
        return script

    def deploy_redis(self) -> dict:
        """
            Deploy Redis
        """
        return {}

    def get_redis_script(self) -> SetupOptions:
        """
            Get the script to deploy Redis
        """
        script = SetupOptions()
        return script

    def deploy_database(self) -> dict:
        """
            Deploy Database
        """
        return {}

    def get_database_script(self) -> SetupOptions:
        """
            Get the script to deploy Database
        """
        script = SetupOptions()
        return script

    def deploy_rabbit(self) -> dict:
        """
            Deploy RabbitMQ
        """
        return {}

    def get_rabbit_script(self) -> SetupOptions:
        """
            Get the script to deploy RabbitMQ
        """
        script = SetupOptions()
        return script
