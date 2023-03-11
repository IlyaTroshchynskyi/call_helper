from common.serializers import ExtendedModelSerializer, StatusMixinSerializer, InfoModelSerializer
from breaks.models.organizations import (
    ReplacementStatus,
    ReplacementEmployee,
    BreakStatus,
    GroupInfo,
    Replacement,
)


class BreakSettingsSerializer(ExtendedModelSerializer):
    class Meta:
        model = GroupInfo
        exclude = ("group",)


class ReplacementShortSerializer(InfoModelSerializer):
    class Meta:
        model = Replacement
        fields = ("id", "date", "break_start", "break_end", "break_max_duration", "min_active")
