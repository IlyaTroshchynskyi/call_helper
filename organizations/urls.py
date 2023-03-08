from django.urls import path, include
from rest_framework.routers import DefaultRouter

from organizations import views

router = DefaultRouter()

router.register(r"positions/", views.PositionView, "positions")


urlpatterns = []

urlpatterns += (path("organisations/", include(router.urls)),)
