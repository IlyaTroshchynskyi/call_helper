from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404

from breaks.factory import ReplacementFactory
from breaks.filters import ReplacementFilter
from breaks.serializers import ReplacementMemberListSerializer
from common.serializers import StatusMixinSerializer
from breaks import serializers
from common.views import ListViewSet, StatusListMixinView, LCRUViewSet, ExtendedRetrieveUpdateAPIView
from breaks.models.organizations import BreakStatus, ReplacementStatus, Replacement, ReplacementMember


@extend_schema_view(
    list=extend_schema(summary="List status of replacements", tags=["Organization"]),
)
class ReplacementStatusView(StatusListMixinView):
    queryset = ReplacementStatus.objects.all()


@extend_schema_view(
    list=extend_schema(summary="List of status launch breaks", tags=["Organization"]),
)
class BreakStatusView(StatusListMixinView):
    queryset = BreakStatus.objects.all()


@extend_schema_view(
    list=extend_schema(summary="List of shifts", tags=["Dinners: Shifts"]),
    retrieve=extend_schema(summary="shift detail", tags=["Dinners: Shifts"]),
    create=extend_schema(summary="Create shift", tags=["Dinners: Shifts"]),
    partial_update=extend_schema(summary="Change shift partially", tags=["Dinners: Shifts"]),
)
class ReplacementView(LCRUViewSet):
    # permission_classes = [IsMyReplacement]

    queryset = Replacement.objects.all()
    serializer_class = serializers.ReplacementListSerializer

    multi_serializer_class = {
        "list": serializers.ReplacementListSerializer,
        "retrieve": serializers.ReplacementRetrieveSerializer,
        "create": serializers.ReplacementCreateSerializer,
        "partial_update": serializers.ReplacementUpdateSerializer,
    }

    http_method_names = ("get", "post", "patch")

    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_class = ReplacementFilter

    def get_queryset(self):
        return ReplacementFactory().list()


@extend_schema_view(
    get=extend_schema(summary="Shift participant data", tags=["Dinners: Shifts"]),
    patch=extend_schema(summary="Change shift member", tags=["Dinners: Shifts"]),
)
class MeReplacementMemberView(ExtendedRetrieveUpdateAPIView):
    queryset = ReplacementMember.objects.all()
    serializer_class = ReplacementMemberListSerializer
    multi_serializer_class = {
        "GET": serializers.ReplacementMemberListSerializer,
        "PATCH": serializers.ReplacementMemberUpdateSerializer,
    }

    def get_object(self):
        user = self.context["request"].user
        replacement_id = self.request.parser_context["kwargs"].get("pk")
        member = get_object_or_404(ReplacementMember, Q(replacement_id=replacement_id, member__employee__user=user))
        return member
