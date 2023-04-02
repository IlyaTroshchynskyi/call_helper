from django.urls import path, include
from rest_framework.routers import DefaultRouter

from organisations import views

router = DefaultRouter()

router.register(r"positions", views.PositionView, "positions")
router.register(r"search", views.OrganisationSearchView, "organisations-search")
router.register(r"(?P<pk>\d+)/employees", views.EmployeeView, "employees")
router.register(r"offers", views.OfferUserView, "user-offers")
router.register(r"(?P<pk>\d+)/offers", views.OfferOrganisationView, "org-offers")
router.register(r"groups/(?P<pk>\d+)/members", views.MemberView, "members")
router.register(r"groups", views.GroupView, "groups")
router.register(r"", views.OrganisationView, "organisations")

urlpatterns = [
    path("organisations/", include(router.urls)),
]
