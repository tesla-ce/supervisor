from django.urls import path, include
from rest_framework import routers

from . import views

admin_router = routers.SimpleRouter()
#admin_router.register(r'status', views.Status, basename='api_admin_status')

api_router = routers.SimpleRouter()

#router.register(r'users', UserViewSet)
#router.register(r'accounts', AccountViewSet)


urlpatterns = [
    path('admin/', include(admin_router.urls)),
    path('status', views.Status.as_view()),
    path('v1/', include(api_router.urls))
]
