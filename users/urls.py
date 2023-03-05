from django.urls import path

from users import views

urlpatterns = [
    path("users/reg/", views.RegistrationView.as_view(), name="reg"),
    path("users/change-passwd", views.ChangePasswordView.as_view(), name="change_passwd"),
    path("users/me/", views.MeView.as_view(), name="me"),
]
