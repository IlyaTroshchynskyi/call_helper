from common.serializers import ExtendedModelSerializer
from organisations.models import Organisation


class OrganisationShortSerializer(ExtendedModelSerializer):
    class Meta:
        model = Organisation
        fields = ("id", "name")
