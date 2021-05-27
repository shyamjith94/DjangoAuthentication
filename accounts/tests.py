import requests
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from utils import random_name

PROFILE_VIEW = "accounts:user_profile"
CREAT_LIST_USER = reverse("accounts:create_list_user")
GROUP_LIST = reverse("accounts:group-list")
GROUP_DETAIL = "accounts:group-detail"


class BaseTest(TestCase):
    def setUp(self) -> None:
        """
        required data initial setup
        """
        self.user_model = get_user_model()
        self.client = APIClient(enforce_csrf_checks=True)
        self.data = dict(
            username="johan2",
            email="john@admaren.com",
            password="asd123####",  # NOSONAR
            first_name="john",
            last_name="wilson",
        )
        self.login_url = reverse("accounts:login_api")
        self.login_res = self.client.post(
            self.login_url,
            data={"username": "johan2", "password": "asd123####"},  # NOSONAR
        )
        self.assertEqual(self.login_res.status_code, status.HTTP_200_OK)
        self.access_token = "JWT {}".format(self.login_res.data.get("access"))  # type: ignore
        self.refresh_token = self.login_res.data.get("refresh")  # type: ignore
        # create initial group
        self.groups_data = dict(name=random_name())
        self.group_res = self.client.post(
            GROUP_LIST, self.groups_data, HTTP_AUTHORIZATION=self.access_token
        )
        self.assertEquals(self.group_res.status_code, status.HTTP_201_CREATED)
        self.group_id = self.group_res.data.get("id")  # type: ignore
        # permission
        permission_url = reverse("accounts:permissions")
        self.permission_res = self.client.get(
            permission_url, HTTP_AUTHORIZATION=self.access_token
        )
        self.assertEquals(self.permission_res.status_code, status.HTTP_200_OK)
        self.assertGreater(len(self.permission_res.data), 0)  # type: ignore
        self.permission_id = self.permission_res.data[0].get("id")  # type: ignore
        # supper init
        super(BaseTest, self).setUp()


class AccountTest(BaseTest):
    """
    test case for account app users login
    """

    def test_create_exists(self):
        api_test_user = self.user_model.objects.get(username=self.data.get("username"))
        self.assertEqual(str(api_test_user), self.data.get("username"))
        self.assertEquals(api_test_user.email, self.data.get("email"))

    def test_login_incorrect(self):
        data = self.data
        data["password"] = "asd"  # NOSONAR
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_access_token(self):
        response = self.client.post(self.login_url, data=self.data, format="json")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_profile(self):
        profile_url = reverse(PROFILE_VIEW)
        response = self.client.get(profile_url, HTTP_AUTHORIZATION=self.access_token)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.data.get("first_name"), response.data.get("first_name"))

    def test_create_user(self):
        data = dict(username="test" + random_name(), password="asd123####",)  # NOSONAR
        create_user_url = "https://auth.admaren.org/api/v1/users/"
        response = requests.post(create_user_url, data=data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_local(self):
        data = dict(username="test" + random_name(), password="asd123####")  # NOSONAR
        response = self.client.post(
            CREAT_LIST_USER, data=data, HTTP_AUTHORIZATION=self.access_token
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_list_user(self):
        response = self.client.get(CREAT_LIST_USER)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertGreater(
            len(response.data), 0
        )  # need one user run above test cases, return list __len__ >0

    def test_user_detail(self):
        detail_url = reverse(PROFILE_VIEW)
        response = self.client.get(detail_url, HTTP_AUTHORIZATION=self.access_token)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data.get("username"), self.data.get("username"))
        self.assertEquals(response.data.get("email"), self.data.get("email"))

    def test_user_update(self):
        data = dict(last_name=random_name())
        patch_url = reverse(PROFILE_VIEW)
        response = self.client.patch(
            patch_url, data=data, HTTP_AUTHORIZATION=self.access_token
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data.get("last_name"), data.get("last_name"))
        self.assertEquals(response.data.get("username"), self.data.get("username"))

    def test_refresh_token(self):
        refresh_url = reverse("accounts:token_refresh")
        data = dict(refresh=self.refresh_token)
        response = self.client.post(
            refresh_url, data=data, HTTP_AUTHORIZATION=self.access_token
        )
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_user_exists(self):
        user_exists = reverse("accounts:users_exists")
        data = dict(username=self.data.get("username"))
        response = self.client.post(user_exists, data=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data.get("detail"), "Exists")

    def test_user_not_exists(self):
        user_exists = reverse("accounts:users_exists")
        data = dict(username="unknown user")
        response = self.client.post(user_exists, data=data)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.data.get("detail"), "Not Exists")


class GroupTest(BaseTest):
    def test_group_create(self):
        data = dict(name=random_name())
        response = self.client.post(
            GROUP_LIST, data, HTTP_AUTHORIZATION=self.access_token
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def test_group_list(self):
        response = self.client.get(GROUP_LIST, HTTP_AUTHORIZATION=self.access_token)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_group_detail(self):
        url = reverse("accounts:group-detail", kwargs={"pk": self.group_id})
        response = self.client.get(url, HTTP_AUTHORIZATION=self.access_token)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_group_patch(self):
        url = reverse(GROUP_DETAIL, kwargs={"pk": self.group_id})
        data = self.groups_data
        data["name"] = random_name()
        response = self.client.patch(url, data, HTTP_AUTHORIZATION=self.access_token)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data.get("name"), data.get("name"))

    def test_permission_listing(self):
        url = reverse("accounts:permissions")
        response = self.client.get(url, HTTP_AUTHORIZATION=self.access_token)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_group_permission_patch(self):
        url = reverse(GROUP_DETAIL, kwargs={"pk": self.group_id})
        data = dict(name=random_name(), permissions=[self.permission_id])
        response = self.client.patch(url, data, HTTP_AUTHORIZATION=self.access_token)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data.get("name"), data.get("name"))

    def test_group_delete(self):
        url = reverse(GROUP_DETAIL, kwargs={"pk": self.group_id})
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.access_token)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_with_roles(self):
        data = dict(
            roles=[self.group_id],
            username=random_name(),
            password="asd123####",  # NOSONAR
            last_name=random_name(),
            first_name=random_name(),
        )
        response = self.client.post(
            CREAT_LIST_USER, data, HTTP_AUTHORIZATION=self.access_token
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
