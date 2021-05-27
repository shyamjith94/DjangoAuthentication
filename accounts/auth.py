from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.auth_state import backend_cls


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        backend = backend_cls()
        validated_token = backend.validate_token(request, raw_token)
        return self.get_user(validated_token), validated_token
