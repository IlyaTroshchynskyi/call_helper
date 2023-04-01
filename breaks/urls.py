from django.urls import path, include
from rest_framework.routers import DefaultRouter

from breaks import views

router = DefaultRouter()

router.register(r"replacements", views.ReplacementView, "replacements")
router.register(r"replacements/(?P<pk>\d+)/schedule", views.BreakScheduleView, "breaks-schedule")
router.register(r"statuses/replacements", views.ReplacementStatusView, "replacement-statuses")


urlpatterns = [
    path("breaks/replacements/<int:pk>/member/", views.MeReplacementMemberView.as_view(), name="replacement-member"),
    path("breaks/replacements/<int:pk>/break/", views.BreakMeView.as_view(), name="break-me"),
    path("organisations/", include(router.urls)),
]
