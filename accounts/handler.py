import requests
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken

from accounts.backends import AuthBackendBase
from accounts.models import User
from core.exceptions import AppException


class BaseAuthHandler(object):
    name = "base_auth_handler"
    CLIENT_ID = "base_client"
    CLIENT_SECRET = settings.OAUTH2_CLIENT_SECRET_KEY
    REQUEST_METHOD = "POST"
    grant_type = "password"
    scope = "identity:users,identity:roles"

    def __init__(self, backend: AuthBackendBase):
        self.backend = backend

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def login_payload(self, username, password):
        payload = {
            "grant_type": self.grant_type,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "username": username,
            "password": password,
            "scope": self.scope,
        }
        return payload

    @classmethod
    def refresh_payload(cls, refresh_token):
        payload = {"refresh": refresh_token}
        return payload

    def login_url(self):
        return self.backend.access_token_url()

    def refresh_url(self):
        return self.backend.refresh_token_url()

    def login(self, username, password, method="POST"):
        response = requests.request(
            method, self.login_url(), data=self.login_payload(username, password),
        )
        auth_response = response.json()
        if response.status_code == 200:
            access_token = AccessToken(auth_response["access"])
            if not User.objects.filter(username=access_token["username"]).exists():
                self.backend.create_new_user(
                    auth_response["access"], password, username
                )
        else:
            raise AppException(auth_response["detail"])
        return auth_response

    def refresh(self, refresh, method="POST"):
        response = requests.request(
            method,
            self.refresh_url(),
            data=self.refresh_payload(refresh_token=refresh),
        )
        auth_response = response.json()
        if response.status_code == 200:
            return auth_response
        else:
            raise AppException(auth_response["detail"])

    def access_token(self, request):
        context = getattr(request, "context", {})
        return context.get("access_token")

    def create_remote_user(self, request, data=None, method="POST"):
        if data is None:
            data = {}
        response = self.backend.create_remote_user(
            self.access_token(request), method, data=data,
        )
        return response


class AdmarenAuthHadler(BaseAuthHandler):
    name = "AdmarenAuthHandler"


class HoppeAuthHadler(BaseAuthHandler):
    name = "HoppeAuthHadler"
