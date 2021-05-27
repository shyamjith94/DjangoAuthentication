from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.conf.urls.static import static


schema_view = get_schema_view(
    openapi.Info(
        title="Secure Load API",
        default_version="v1",
        description="Loading Computer",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="info@admaren.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    re_path(
        r"^api/swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^api/swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api/admin/", admin.site.urls),
    path(
        "api/", include("accounts.urls", namespace="accounts")
    ),  # user management urls
    path(
        "api/", include("apps.vessel.urls", namespace="vessel")
    ),  # vessel management urls
    path(
        "api/", include("apps.project.urls", namespace="project")
    ),  # project management urls
    path("api/", include("core.urls", namespace="core")),  # Core management urls
    path("api/", include("apps.sdc.urls", namespace="sdc")),  # SDC management urls
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
