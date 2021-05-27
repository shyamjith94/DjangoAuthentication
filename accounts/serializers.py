from rest_framework import serializers
from rest_framework_simplejwt.serializers import PasswordField
from django.contrib.auth.models import Group
from .auth_state import auth_handler
from .models import User
import requests
from rest_framework import status
from django.contrib.auth.models import Permission
from rest_framework.exceptions import APIException
from django.contrib.auth.hashers import check_password


class PasswordChange(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Old password mismatch "
    default_code = "bad_request"


class HoppeServerError(APIException):
    status_code = 500
    default_detail = "Can't change password now hoppe server error"
    default_code = "hoppe_server_error"


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = PasswordField()

    def validate(self, attrs):
        data = super().validate(attrs)
        aut_response = auth_handler.login(**data)
        return aut_response


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        data = super().validate(attrs)
        aut_response = auth_handler.refresh(**data)
        return aut_response


class GroupsGetDetailSerializer(serializers.ModelSerializer):
    """
    list users data serializes
    """

    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]
        read_only_field = ["id"]

    def get_permissions(self, instance):
        return PermissionSerializer(instance.permissions, many=True).data


class GroupsCreateUpdateSerializer(serializers.ModelSerializer):
    """
    list users data serializes
    """

    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]
        read_only_field = ["id"]

    def to_representation(self, instance):
        return GroupsGetDetailSerializer(instance).data


class PermissionSerializer(serializers.ModelSerializer):
    """
    list users data serializes
    """

    app_label = serializers.SerializerMethodField()
    app_model = serializers.SerializerMethodField()
    content_id = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "content_id", "app_label", "app_model"]
        read_only_field = "__all__"

    def get_app_label(self, instance):
        return instance.content_type.app_label

    def get_app_model(self, instance):
        return instance.content_type.model

    def get_content_id(self, instance):
        return instance.content_type.id


class UserDetailSerializer(serializers.ModelSerializer):
    """
    user profile information serializes
    """

    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "is_active",
            "roles",
        ]

    def get_roles(self, instance):
        """
        return user roles
        """
        return GroupsGetDetailSerializer(instance.groups, many=True).data


class UserCreateSerializer(serializers.ModelSerializer):
    """
    create user object serializes
    """

    class Meta:
        model = User
        fields = ["username", "password", "email", "first_name", "last_name", "groups"]

    def create(self, validated_data):
        password = validated_data.get("password")
        user = super(UserCreateSerializer, self).create(validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_internal_value(self, data):
        """
        change name groups to roles
        """
        if "roles" in data:
            groups = data.pop("roles")
            data["groups"] = groups
            return data
        return data


class UsersListSerializer(serializers.ModelSerializer):
    """
    list users data serializes
    """

    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "roles",
        ]
        read_only_field = ["id"]

    def get_roles(self, instance):
        """
        return user roles
        """
        return GroupsGetDetailSerializer(instance.groups, many=True).data


class RetrieveUpdateSerializer(serializers.ModelSerializer):
    """
    create user object serializes
    """

    roles = serializers.SerializerMethodField()
    old_password = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "old_password",
            "email",
            "first_name",
            "last_name",
            "roles",
        ]

    def get_roles(self, instance):
        """
        return user roles
        """
        return GroupsGetDetailSerializer(instance.groups, many=True).data

    def to_representation(self, instance):
        """
        return list users data serializes
        """
        return UsersListSerializer(instance).data

    def to_internal_value(self, data):
        """
        change name groups to roles
        """
        if "roles" in data:
            groups = data.pop("roles")
            data["groups"] = groups
            return data
        return data

    def validate(self, attrs):
        password = attrs.get("password")
        old_password = attrs.get("old_password")
        if "password" in attrs and "old_password" in attrs:
            if not check_password(
                old_password, self.context.get("request").user.password
            ):
                raise PasswordChange()
            request_data = self.context.get("request")
            access_token = request_data.META["HTTP_AUTHORIZATION"]
            data = dict(password=password)
            header = dict(HTTP_AUTHORIZATION=access_token)

            url = (
                f"https://auth.admaren.org/api/v1/users/{self.context['request'].user}/"
            )
            response = requests.patch(url, data=data, headers=header)
            if response.status_code != 200:
                raise HoppeServerError()
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.get("password")
        user = super(RetrieveUpdateSerializer, self).update(instance, validated_data)
        user.set_password(password)
        user.save()
        return user
