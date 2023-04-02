from common.serializers import DictMixinSerializer
from organisations.models import Position


class PositionShortSerializer(DictMixinSerializer):
    class Meta:
        model = Position
