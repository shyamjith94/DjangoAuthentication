from django.urls import path, include
from rest_framework import routers
from accounts import views

app_name = "accounts"

router = routers.DefaultRouter()
router.register(r"v1/roles", views.GroupsAPiView, basename="group")
urlpatterns = [
    path("v1/token/refresh/", views.RefreshAPIView.as_view(), name="token_refresh"),
    path("v1/login/", views.LoginAPIView.as_view(), name="login_api"),
    path("v1/profile/", views.UserProfileAPIView.as_view(), name="user_profile"),
    path("v1/users/", views.CreateListUserApiView.as_view(), name="create_list_user"),
    path(
        "v1/users/<int:pk>/",
        views.RetrieveUpdateUserApiView.as_view(),
        name="update_user",
    ),
    path("v1/users-exists/", views.UserExistsApiView.as_view(), name="users_exists"),
    path("v1/permissions/", views.PermissionApiView.as_view(), name="permissions"),
    path("", include(router.urls)),  # group urls
]
