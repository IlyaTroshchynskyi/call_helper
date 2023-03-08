from django.urls import path, include
from rest_framework.routers import DefaultRouter

from organizations import views

router = DefaultRouter()

router.register(r"positions", views.PositionView, "positions")
router.register(r"search", views.OrganisationSearchView, "organisations-search")
router.register(r"manage", views.OrganisationView, "organisations")
router.register(r"manage/<?P<pk>\d+/employees", views.EmployeeView, "organisations")

urlpatterns = [
    path("organisations/", include(router.urls)),
]
