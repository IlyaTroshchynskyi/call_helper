from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users import views

router = DefaultRouter()

router.register(r"search", views.UserListSearchView, "users-search")


urlpatterns = [
    path("users/reg/", views.RegistrationView.as_view(), name="reg"),
    path("users/change-passwd/", views.ChangePasswordView.as_view(), name="change_passwd"),
    path("users/me/", views.MeView.as_view(), name="me"),
]

urlpatterns += (path("users/", include(router.urls)),)
