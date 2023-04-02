from common.serializers import ExtendedModelSerializer
from organisations.models import Group

from organisations.serializers.api import EmployeeShortSerializer
from organisations.serializers.api import OrganisationShortSerializer


class GroupShortSerializer(ExtendedModelSerializer):
    organisation = OrganisationShortSerializer()
    manager = EmployeeShortSerializer()

    class Meta:
        model = Group
        fields = ("id", "name", "organisation", "manager")
