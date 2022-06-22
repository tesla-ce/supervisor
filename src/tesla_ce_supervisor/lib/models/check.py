import typing
import json


class ServiceDeploymentInformation:
    def __init__(self, name: str,
                 orchestrator: typing.Optional[str] = None,
                 info: typing.Optional[dict] = None) -> None:
        super().__init__()

        self.name: str = name
        self.orchestrator: str = orchestrator
        self.jobs_expected: int = 0
        self.jobs_running: int = 0
        self.jobs_healthy: int = 0
        self.info: typing.Optional[dict] = info
        self.status: typing.Optional[typing.Union[typing.Literal['waiting'],
                                                  typing.Literal['success'],
                                                  typing.Literal['error']]] = None

    def is_valid(self) -> bool:
        return self.status == 'success'

    def get_jobs(self) -> dict:
        return {
            'expected': self.jobs_expected,
            'running': self.jobs_running,
            'healthy': self.jobs_healthy,
        }

    def to_json(self):
        info = None
        if self.info is not None:
            info = json.dumps(self.info)
        return {
            'name': self.name,
            'orchestrator': self.orchestrator,
            'jobs': self.get_jobs(),
            'status': self.status,
            'info': info
        }


class ServiceCatalogInformation:
    def __init__(self, name: str, catalog: typing.Optional[str]) -> None:
        super().__init__()

        self.name: str = name
        self.catalog: str = catalog
        self.instances_total: int = 0
        self.instances_healthy: int = 0
        self.services = []
        self.info: typing.Optional[dict] = None

    def is_healthy(self) -> bool:
        return self.instances_total == self.instances_healthy

    def get_instances(self):
        return {
                'total': self.instances_total,
                'healthy': self.instances_healthy
            }

    def to_json(self):
        info = None
        if self.info is not None:
            info = json.dumps(self.info)
        return {
            'name': self.name,
            'services': self.services,
            'instances': self.get_instances(),
            'healthy': self.is_healthy(),
            'info': info
        }


class ServiceStatus:

    def __init__(self,
                 deployment: typing.Optional[ServiceDeploymentInformation] = None,
                 catalog: typing.Optional[ServiceCatalogInformation] = None,
                 ) -> None:
        super().__init__()
        self.deploy_info: typing.Optional[ServiceDeploymentInformation] = deployment
        self.catalog_info: typing.Optional[ServiceCatalogInformation] = catalog

    def is_valid(self) -> bool:
        if self.deploy_info is None or self.catalog_info is None:
            return False
        return self.deploy_info.is_valid() and self.catalog_info.is_healthy()

    def get_jobs(self) -> dict:
        jobs = None
        if self.deploy_info is not None:
            jobs = self.deploy_info.get_jobs()
        return jobs

    def get_instances(self) -> dict:
        instances = None
        if self.catalog_info is not None:
            instances = self.catalog_info.get_instances()
            instances['services'] = self.catalog_info.services
        return instances

    def get_orchestrator(self) -> typing.Optional[str]:
        if self.deploy_info is not None:
            return self.deploy_info.orchestrator
        return None

    def get_catalog(self) -> typing.Optional[str]:
        if self.catalog_info is not None:
            return self.catalog_info.catalog
        return None

    def to_json(self):
        deploy_info = None
        if self.deploy_info is not None:
            deploy_info = self.deploy_info.to_json()
        catalog_info = None
        if self.catalog_info is not None:
            catalog_info = self.catalog_info.to_json()
        return {
            'orchestrator': self.get_orchestrator(),
            'catalog': self.get_catalog(),
            'instances': self.get_instances(),
            'jobs': self.get_jobs(),
            'valid': self.is_valid(),
            'info': {
                'deploy': deploy_info,
                'catalog': catalog_info
            }
        }


class ConnectionStatus:
    pass
