from django.urls import path, include
from rest_framework import routers

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

admin_router = routers.SimpleRouter()
#admin_router.register(r'status', views.Status, basename='api_admin_status')

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
