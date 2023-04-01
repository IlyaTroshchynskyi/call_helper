from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from breaks.factory import ReplacementFactory
from breaks.filters import ReplacementFilter
from breaks.serializers.api import ReplacementMemberListSerializer
from common.serializers import StatusMixinSerializer
from breaks.serializers import api, breaks
from common.services import get_schedule_time_title
from common.views import (
    ListViewSet,
    StatusListMixinView,
    LCRUViewSet,
    ExtendedRetrieveUpdateAPIView,
    ExtendedCRUAPIView,
)
from breaks.models.organizations import BreakStatus, ReplacementStatus, Replacement, ReplacementMember, Break


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
    serializer_class = api.ReplacementListSerializer

    multi_serializer_class = {
        "list": api.ReplacementListSerializer,
        "retrieve": api.ReplacementRetrieveSerializer,
        "create": api.ReplacementCreateSerializer,
        "partial_update": api.ReplacementUpdateSerializer,
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
        "GET": api.ReplacementMemberListSerializer,
        "PATCH": api.ReplacementMemberUpdateSerializer,
    }

    def get_object(self):
        user = self.context["request"].user
        replacement_id = self.request.parser_context["kwargs"].get("pk")
        member = get_object_or_404(ReplacementMember, Q(replacement_id=replacement_id, member__employee__user=user))
        return member


@extend_schema_view(
    get=extend_schema(summary="Dinner detail", tags=["Dinners: User Dinners"]),
    post=extend_schema(summary="Lunch reservation", tags=["Dinners: User Dinners"]),
    patch=extend_schema(summary="Lunch reservation change", tags=["Dinners: User Dinners"]),
)
class BreakMeView(ExtendedCRUAPIView):
    # permission_classes = [IsNotCorporate]
    queryset = Break.objects.all()
    serializer_class = breaks.BreakMeUpdateSerializer
    multi_serializer_class = {
        "GET": breaks.BreakMeRetrieveSerializer,
    }
    http_method_names = ("get", "post", "patch")

    def get_object(self):
        user = self.request.user
        replacement_id = self.request.parser_context["kwargs"].get("pk")
        return get_object_or_404(Break, Q(replacement_id=replacement_id, member__member__employee__user=user))


@extend_schema_view(
    list=extend_schema(summary="Lunch Schedule", tags=["Lunches: Lunches"]),
)
class BreakScheduleView(ListViewSet):
    # permission_classes = [IsNotCorporate]
    queryset = Break.objects.all()
    serializer_class = breaks.BreakScheduleSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        replacement_id = self.request.parser_context["kwargs"].get("pk")
        replacement = get_object_or_404(Replacement, id=replacement_id)
        title = get_schedule_time_title(replacement.break_start, replacement.break_end, "Employee")
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(qs, many=True).data
        serializer.insert(0, title)
        return Response(serializer)

    def get_queryset(self):
        replacement_id = self.request.parser_context["kwargs"].get("pk")
        return Break.objects.prefetch_related(
            "member",
            "member__member",
            "member__member__employee",
            "member__member__employee__user",
        ).filter(replacement_id=replacement_id)
