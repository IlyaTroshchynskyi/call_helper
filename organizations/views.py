from drf_spectacular.utils import extend_schema_view, extend_schema

from common.views import StatusListMixinView
from organizations.models import Position


@extend_schema_view(
    list=extend_schema(summary="List of positions", tags=["Organization"]),
)
class PositionView(StatusListMixinView):
    queryset = Position.objects.all()
