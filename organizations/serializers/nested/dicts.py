from common.serializers import DictMixinSerializer
from organizations.models import Position


class PositionShortSerializer(DictMixinSerializer):
    class Meta:
        model = Position
