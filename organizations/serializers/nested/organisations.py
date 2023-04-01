from common.serializers import ExtendedModelSerializer
from organizations.models import Organization


class OrganisationShortSerializer(ExtendedModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name")
