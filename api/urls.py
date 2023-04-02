from django.urls import path, include

from api.spectacular.urls import urlpatterns as doc_urls
from users.urls import urlpatterns as users_urls
from organisations.urls import urlpatterns as organisation_urls
from breaks.urls import urlpatterns as break_urls

app_name = "api"

urlpatterns = [
    path("auth/", include("djoser.urls.jwt")),
]

urlpatterns += doc_urls
urlpatterns += users_urls
urlpatterns += organisation_urls
urlpatterns += break_urls
