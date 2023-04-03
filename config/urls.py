from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls"), name="api"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("__debug__/", include("debug_toolbar.urls")),
    path("rest/", include("users.urls")),
    path("rest/", include("organisation.urls")),
    path("rest/", include("breaks.urls")),
]
