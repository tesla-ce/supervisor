import os
import typing
from urllib.parse import urlparse
from django.template.loader import render_to_string
from .base import BaseDeploy
from ..tesla.conf import Config


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

    def __init__(self, nomad_addr: typing.Optional[str] = 'http://127.0.0.1:4646',
                 nomad_region: typing.Optional[str] = 'global',
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
        self.nomad_datacenters = nomad_datacenters
        if self.nomad_datacenters is None:
            self.nomad_datacenters = []
        self.nomad_auth = nomad_auth

        # Check default environment variables
        if nomad_addr is not None:
            parsed = urlparse(nomad_addr)
            self.nomad_url = ''
            if parsed.scheme is not None and len(parsed.scheme) > 0:
                self.nomad_url += '{}://'.format(parsed.scheme)
            self.nomad_url += '{}'.format(parsed.hostname)
            self.nomad_port = parsed.port

        self.nomad_region = os.getenv('NOMAD_REGION', nomad_region)
        self.nomad_token = os.getenv('NOMAD_TOKEN', nomad_token)
        self.nomad_client_cert = os.getenv('NOMAD_CLIENT_CERT', nomad_client_cert)
        self.nomad_client_key = os.getenv('NOMAD_CLIENT_KEY', nomad_client_key)
        self.nomad_cacert = os.getenv('NOMAD_CACERT', nomad_cacert)
        self.nomad_capath = os.getenv('NOMAD_CAPATH', nomad_capath)
        self.nomad_skip_verify = os.getenv('NOMAD_SKIP_VERIFY', nomad_skip_verify)
        self.nomad_tls_server_name = os.getenv('NOMAD_TLS_SERVER_NAME', nomad_tls_server_name)


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
            self.nomad_conf = NomadConfig()
        self._client = nomad.Nomad()

    def write_scripts(self) -> None:
        pass

    def deploy_lb(self) -> None:
        """
            Deploy Load Balancer
        """

        context = {}
        script = self._remove_empty_lines(render_to_string('lb/traefik/nomad/traefik.nomad', context))


        pass

    def get_lb_script(self) -> dict:
        """
            Get the script to deploy Load Balancer
        """
        pass

    def deploy_vault(self) -> None:
        """
            Deploy Hashicorp Vault
        """
        pass

    def get_vault_script(self) -> dict:
        """
            Get the script to deploy Hashicorp Vault
        """
        return {}

    def deploy_minio(self) -> None:
        """
            Deploy MinIO
        """
        pass

    def get_minio_script(self) -> dict:
        """
            Get the script to deploy MinIO
        """
        return {}

    def deploy_redis(self) -> None:
        """
            Deploy Redis
        """
        pass

    def get_redis_script(self) -> dict:
        """
            Get the script to deploy Redis
        """
        return {}

    def deploy_database(self) -> None:
        """
            Deploy Database
        """
        pass

    def get_database_script(self) -> dict:
        """
            Get the script to deploy Database
        """
        return {}

    def deploy_rabbit(self) -> None:
        """
            Deploy RabbitMQ
        """
        pass

    def get_rabbit_script(self) -> dict:
        """
            Get the script to deploy RabbitMQ
        """
        return {}
