class ServiceStatus:

    instances = 0
    jobs = 0
    valid = False
    deploy_info = None
    catalog_info = None

    def to_json(self):
        return {
            'instances': self.instances,
            'jobs': self.jobs,
            'valid': self.valid,
            'info': {
                'deploy': self.deploy_info,
                'catalog': self.catalog_info
            }
        }
