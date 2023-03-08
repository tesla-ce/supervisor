from django.urls import path

from . import config
from . import connection
from . import deploy
from . import check
from . import task
from . import vault
from . import log

urlpatterns = [
    # Load Balancer
    path('deploy/lb', deploy.APIDeployLoadBalancer.as_view(), name='setup_api_deploy_lb'),
    # Services Deployment
    path('deploy/database', deploy.APIDeployDatabase.as_view(), name='setup_api_deploy_database'),
    path('deploy/minio', deploy.APIDeployMinio.as_view(), name='setup_api_deploy_minio'),
    path('deploy/rabbitmq', deploy.APIDeployRabbitMQ.as_view(), name='setup_api_deploy_rabbitmq'),
    path('deploy/redis', deploy.APIDeployRedis.as_view(), name='setup_api_deploy_redis'),
    path('deploy/vault', deploy.APIDeployVault.as_view(), name='setup_api_deploy_vault'),
    path('deploy/tesla/api', deploy.APIDeployAPI.as_view(), name='setup_api_deploy_tesla_api'),
    path('deploy/tesla/beat', deploy.APIDeployBeat.as_view(), name='setup_api_deploy_tesla_beat'),
    path('deploy/tesla/worker-all', deploy.APIDeployAPIWorkerAll.as_view(), name='setup_api_deploy_tesla_worker_all'),
    path('deploy/tesla/worker-enrolment', deploy.APIDeployAPIWorkerEnrolment.as_view(),
         name='setup_api_deploy_tesla_worker_enrolment'),
    path('deploy/tesla/worker-enrolment-storage', deploy.APIDeployAPIWorkerEnrolmentStorage.as_view(),
         name='setup_api_deploy_tesla_worker_enrolment_storage'),
    path('deploy/tesla/worker-enrolment-validation', deploy.APIDeployAPIWorkerEnrolmentValidation.as_view(),
         name='setup_api_deploy_tesla_worker_enrolment_validation'),
    path('deploy/tesla/worker-verification', deploy.APIDeployAPIWorkerVerification.as_view(),
         name='setup_api_deploy_tesla_worker_verification'),
    path('deploy/tesla/worker-alerts', deploy.APIDeployAPIWorkerAlerts.as_view(),
         name='setup_api_deploy_tesla_worker_alerts'),
    path('deploy/tesla/worker-reporting', deploy.APIDeployAPIWorkerReporting.as_view(),
         name='setup_api_deploy_tesla_worker_reporting'),
    path('deploy/tesla/lapi', deploy.APIDeployLAPI.as_view(), name='setup_api_deploy_tesla_lapi'),
    path('deploy/tesla/dashboard', deploy.APIDeployDashboard.as_view(), name='setup_api_deploy_tesla_dashboard'),
    path('deploy/tesla/moodle', deploy.APIDeployMoodle.as_view(), name='setup_api_deploy_tesla_moodle'),
    path('deploy/tesla/fr', deploy.APIDeployFR.as_view(), name='setup_api_deploy_tesla_fr'),
    path('deploy/tesla/ks', deploy.APIDeployKS.as_view(), name='setup_api_deploy_tesla_ks'),
    path('deploy/tesla/tpt', deploy.APIDeployTPT.as_view(), name='setup_api_deploy_tesla_tpt'),
    # Check
    path('check/dns', check.APICheckDNS.as_view(), name='setup_api_check_dns'),
    path('check/lb', check.APICheckLoadBalancer.as_view(), name='setup_api_check_lb'),
    path('check/database', check.APICheckDatabase.as_view(), name='setup_api_check_database'),
    path('check/minio', check.APICheckMinio.as_view(), name='setup_api_check_minio'),
    path('check/rabbitmq', check.APICheckRabbitMQ.as_view(), name='setup_api_check_rabbitmq'),
    path('check/redis', check.APICheckRedis.as_view(), name='setup_api_check_redis'),
    path('check/vault', check.APICheckVault.as_view(), name='setup_api_check_vault'),
    path('check/tesla/api', check.APICheckAPI.as_view(), name='setup_api_check_tesla_api'),
    path('check/tesla/beat', check.APICheckBeat.as_view(), name='setup_api_check_tesla_beat'),
    path('check/tesla/worker-all', check.APICheckAPIWorkerAll.as_view(), name='setup_api_check_tesla_worker_all'),
    path('check/tesla/worker-enrolment', check.APICheckAPIWorkerEnrolment.as_view(), name='setup_api_check_tesla_worker_enrolment'),
    path('check/tesla/worker-enrolment-storage', check.APICheckAPIWorkerEnrolmentStorage.as_view(), name='setup_api_check_tesla_worker_enrolment_storage'),
    path('check/tesla/worker-enrolment-validation', check.APICheckAPIWorkerEnrolmentValidation.as_view(), name='setup_api_check_tesla_worker_enrolment_validation'),
    path('check/tesla/worker-verification', check.APICheckAPIWorkerVerification.as_view(), name='setup_api_check_tesla_worker_enrolment_verification'),
    path('check/tesla/worker-alerts', check.APICheckAPIWorkerAlerts.as_view(), name='setup_api_check_tesla_worker_enrolment_alerts'),
    path('check/tesla/worker-reporting', check.APICheckAPIWorkerReporting.as_view(), name='setup_api_check_tesla_worker_enrolment_reporting'),
    path('check/tesla/lapi', check.APICheckLAPI.as_view(), name='setup_api_check_tesla_lapi'),
    path('check/tesla/dashboard', check.APICheckDashboard.as_view(), name='setup_api_check_tesla_dashboard'),
    path('check/tesla/moodle', check.APICheckMoodle.as_view(), name='setup_api_check_tesla_moodle'),
    path('check/tesla/fr', check.APICheckFR.as_view(), name='setup_api_check_tesla_fr'),
    path('check/tesla/ks', check.APICheckKS.as_view(), name='setup_api_check_tesla_ks'),
    path('check/tesla/tpt', check.APICheckTPT.as_view(), name='setup_api_check_tesla_tpt'),

    # TeSLA CE Supervisor
    path('deploy/supervisor', deploy.APIDeploySupervisor.as_view(), name='setup_api_deploy_supervisor'),
    path('check/supervisor', check.APICheckSupervisor.as_view(), name='setup_api_check_supervisor'),

    # Vault Configuration
    path('vault/kv', vault.APIVaultInitKV.as_view(), name='setup_api_vault_kv'),

    # Connection
    path('connection/vault', connection.APIConnectionVault.as_view(), name='setup_api_connection_vault'),
    path('connection/database', connection.APIConnectionDatabase.as_view(), name='setup_api_connection_database'),
    path('connection/rabbitmq', connection.APIConnectionRabbitmq.as_view(), name='setup_api_connection_rabbitmq'),
    path('connection/redis', connection.APIConnectionRedis.as_view(), name='setup_api_connection_redis'),
    path('connection/supervisor', connection.APIConnectionSupervisor.as_view(), name='setup_api_connection_supervisor'),
    path('connection/minio', connection.APIConnectionMinIO.as_view(), name='setup_api_connection_minio'),

    # Config
    path('config/vault', config.APIConfigVault.as_view(), name='setup_api_config_vault'),
    path('config/database', config.APIConfigDatabase.as_view(), name='setup_api_config_database'),
    path('config/rabbitmq', config.APIConfigRabbitmq.as_view(), name='setup_api_config_rabbitmq'),
    path('config/redis', config.APIConfigRedis.as_view(), name='setup_api_config_redis'),
    path('config/supervisor', config.APIConfigSupervisor.as_view(), name='setup_api_config_supervisor'),
    path('config/minio', config.APIConfigMinIO.as_view(), name='setup_api_config_minio'),
    path('config/tesla/<str:step>', config.APIConfigTeSLA.as_view(), name='setup_api_config_tesla'),

    path('task/config/<str:step>', task.APITaskConfig.as_view(), name='setup_api_task_config'),
    path('task/log', log.APILogConfig.as_view(), name='setup_api_log_config'),
]
