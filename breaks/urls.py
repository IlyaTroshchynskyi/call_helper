from django.urls import path, include
from rest_framework.routers import DefaultRouter

from breaks import views

router = DefaultRouter()

router.register(r"statuses/breaks", views.BreakStatusView, "breaks-statuses")
router.register(r"statuses/replacements", views.ReplacementStatusView, "replacement-statuses")


urlpatterns = []

urlpatterns += (path("organisations/", include(router.urls)),)
