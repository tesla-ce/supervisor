from rest_framework_simplejwt.authentication import JWTAuthentication


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
