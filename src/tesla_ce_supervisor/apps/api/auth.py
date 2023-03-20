from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from django.contrib.auth import get_user_model


def _initialize_authentication():
    """
        Initialize authentication
    """
    if settings.SUPERVISOR_ADMIN_USER is not None and settings.SUPERVISOR_ADMIN_PASSWORD is not None:
        try:
            get_user_model().objects.get(username=settings.SUPERVISOR_ADMIN_USER)
        except get_user_model().DoesNotExist:
            # Create the administrator user
            if get_user_model().objects.count() == 0:
                get_user_model().objects.create_superuser(
                    username=settings.SUPERVISOR_ADMIN_USER,
                    password=settings.SUPERVISOR_ADMIN_PASSWORD,
                    email=settings.SUPERVISOR_ADMIN_EMAIL
                )


class SupervisorJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        return super().authenticate(request)

    def authenticate_header(self, request):
        return super().authenticate_header(request)

    def get_header(self, request):
        return super().get_header(request)

    def get_raw_token(self, header):
        return super().get_raw_token(header)

    def get_validated_token(self, raw_token):
        return super().get_validated_token(raw_token)

    def get_user(self, validated_token):
        return super().get_user(validated_token)
