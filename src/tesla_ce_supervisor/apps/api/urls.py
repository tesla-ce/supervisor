from django.urls import path, include
from rest_framework import routers

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from .auth import _initialize_authentication
# Initialize authentication for API
_initialize_authentication()


admin_router = routers.SimpleRouter()
admin_router.register(r'status', views.admin.StatusViewSet, basename='api_admin_status')
admin_router.register(r'connection', views.admin.ConnectionViewSet, basename='api_admin_connection')
admin_router.register(r'config', views.admin.ConfigViewSet, basename='api_admin_config')
admin_router.register(r'task', views.admin.TaskViewSet, basename='api_admin_task')

api_router = routers.SimpleRouter()

#router.register(r'users', UserViewSet)
#router.register(r'accounts', AccountViewSet)


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', include(admin_router.urls)),
    path('status', views.Status.as_view()),
    path('v1/', include(api_router.urls))
]
