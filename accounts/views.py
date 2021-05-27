from django.db.models import QuerySet
from rest_framework import status
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    RetrieveUpdateAPIView,
    get_object_or_404,
)
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth.models import Group
from core.exceptions import AppException
from core.pagination import GenericListingPagination

from .auth_state import auth_handler
from .models import User
from .serializers import (
    LoginSerializer,
    RefreshTokenSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UsersListSerializer,
    GroupsGetDetailSerializer,
    RetrieveUpdateSerializer,
    PermissionSerializer,
    GroupsCreateUpdateSerializer,
)
from django.contrib.auth.models import Permission


class RefreshAPIView(TokenRefreshView):
    """Refresh API

    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """

    permission_classes = [AllowAny]
    serializer_class = RefreshTokenSerializer


class LoginAPIView(GenericAPIView):
    """Login API

    Authenticates the user credentials and respond with valid
    access token and refresh token.

    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid()
        except Exception as e:
            raise AppException(str(e))
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserProfileAPIView(RetrieveUpdateAPIView):
    """User Profile API

    Return the detailed information of the authenticated user.
    Update user information.

    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user


class CreateListUserApiView(ListCreateAPIView, RetrieveUpdateAPIView):
    """
    create user object return request data.
    """

    permission_classes = [AllowAny]
    queryset = User.objects.all()
    pagination_class = GenericListingPagination
    lookup_field = "pk"

    def get_serializer_class(self):
        """
        switching serializer class. request method
        """
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return UserCreateSerializer
        return UsersListSerializer

    def perform_create(self, serializer):
        # create user in the auth server
        auth_handler.create_remote_user(
            request=self.request, data=serializer.validated_data
        )
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        serializer = UserDetailSerializer(user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class RetrieveUpdateUserApiView(RetrieveUpdateAPIView):
    """
    create user object return request data.
    """

    permission_classes = [AllowAny]
    queryset = User.objects.all()
    pagination_class = GenericListingPagination
    lookup_field = "pk"

    def get_serializer_class(self):
        """
        switching serializer class. request method
        """
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return RetrieveUpdateSerializer
        return UsersListSerializer

    def get_serializer_context(self):
        context = super(RetrieveUpdateUserApiView, self).get_serializer_context()
        context.update({"request": self.request})
        return context


class UserExistsApiView(APIView):
    """
    check user object exists return exits or not.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        try:
            User.objects.get(username=username)  # retrieve the user using username
        except User.DoesNotExist:
            return Response(
                data={"detail": "Not Exists"}, status=status.HTTP_404_NOT_FOUND
            )
        else:
            return Response(
                data={"detail": "Exists"}, status=status.HTTP_200_OK
            )  # Otherwise, return True


class GroupsAPiView(ModelViewSet):
    """
    handle CRUD api for  User group/role
    """

    serializer_class = GroupsGetDetailSerializer
    queryset = Group.objects.all()
    pagination_class = GenericListingPagination

    def get_serializer_class(self):
        """
        switching serializer class. request method
        """
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return GroupsCreateUpdateSerializer
        return GroupsGetDetailSerializer


class PermissionApiView(ListCreateAPIView):
    """
    list django model permissions
    """

    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
    pagination_class = GenericListingPagination
