from drf_spectacular.utils import extend_schema_view, extend_schema

from common.serializers import StatusMixinSerializer
from common.views import ListViewSet, StatusListMixinView
from breaks.models.organizations import BreakStatus, ReplacementStatus


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
