from django.urls import path

from . import deploy
from . import vault

urlpatterns = [
    # Load Balancer
    path('deploy/lb', deploy.APIDeployLoadBalancer.as_view(), name='setup_api_deploy_lb'),
    # Services Deployment
    path('deploy/database', deploy.APIDeployDatabase.as_view(), name='setup_api_deploy_database'),
    path('deploy/minio', deploy.APIDeployMinio.as_view(), name='setup_api_deploy_minio'),
    path('deploy/rabbitmq', deploy.APIDeployRabbitMQ.as_view(), name='setup_api_deploy_rabbitmq'),
    path('deploy/redis', deploy.APIDeployRedis.as_view(), name='setup_api_deploy_redis'),
    path('deploy/vault', deploy.APIDeployVault.as_view(), name='setup_api_deploy_vault'),
    # Vault Configuration
    path('vault/kv', vault.APIVaultInitKV.as_view(), name='setup_api_vault_kv'),
]
