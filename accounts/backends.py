import requests
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.exceptions import AppException

from .models import User

GET = "GET"
POST = "POST"


def request(method, url, **kwargs):
    response = requests.request(method, url, **kwargs)
    if response.status_code > 399:
        raise AppException("Authorization Server Error")
    return response.json()


class AuthBackendBase(JWTAuthentication):
    name = "Auth-Base-Backend"
    API_URL = ""
    AUTH_HEADER_TYPE = "JWT"
    ACCESS_TOKEN_PATH = "login"
    REFRESH_TOKEN_PATH = "token/refresh"
    USER_PROFILE = "profile"
    ACCESS_TOKEN_METHOD = "POST"
    SCOPE_SEPARATOR = ","
    user_fields = ["first_name", "last_name", "email", "is_active"]
    API_MAP = {"create_user": "users"}

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @classmethod
    def base_url(cls, version="v1"):
        return f"{cls.API_URL}/{version}"

    @classmethod
    def construct_api(cls, path):
        return f"{cls.base_url()}/{path}/"

    @classmethod
    def access_token_url(cls):
        return cls.construct_api(cls.ACCESS_TOKEN_PATH)

    @classmethod
    def refresh_token_url(cls):
        return cls.construct_api(cls.REFRESH_TOKEN_PATH)

    @classmethod
    def user_api_path(cls):
        return f"{cls.USER_PROFILE}"

    @classmethod
    def auth_header(cls, access_token):
        return {"Authorization": f"{cls.AUTH_HEADER_TYPE} {access_token}"}

    def validate_token(self, request, raw_token):
        validated_token = self.get_validated_token(raw_token)
        access_token = raw_token.decode("utf-8")
        self.authorize(request, access_token)
        context = {"access_token": access_token}
        setattr(request, "context", context)
        return validated_token

    @classmethod
    def user_detail(cls, access_token, method=GET, *args, **kwargs):
        user_info = request(
            method,
            cls.construct_api(cls.user_api_path()),
            headers=cls.auth_header(access_token),
        )
        return user_info

    @classmethod
    def create_remote_user(cls, access_token, method, data):
        user_info = request(
            method,
            cls.construct_api(cls.API_MAP["create_user"]),
            data=data,
            headers=cls.auth_header(access_token),
        )
        return user_info

    def authorize(self, request, access_token):
        """Authorization logic

        * Update user data
        * Raise Auth errors

        """
        user_info = self.user_detail(access_token)
        # TODO : update user data
        return user_info

    @classmethod
    def create_new_user(cls, access_token, password, username):
        # TODO : later move to storage package
        user_info = cls.user_detail(access_token)
        kwargs = {"username": username, "password": password}
        for field in cls.user_fields:
            kwargs[field] = user_info[field]
        user = User.objects.create(**kwargs)
        return user


class AdmarenAuthBackend(AuthBackendBase):
    name = "Admaren-Auth-Backend"
    API_URL = "https://auth.admaren.org/api"


class HoppeAuthBackend(AuthBackendBase):
    name = "Hoppe-Auth-Backend"
