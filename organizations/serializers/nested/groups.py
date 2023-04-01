from common.serializers import ExtendedModelSerializer
from organizations.models import Group

# from organizations.serializers.api import EmployeeShortSerializer
# from organizations.serializers.api import OrganisationShortSerializer


class GroupShortSerializer(ExtendedModelSerializer):
    pass
    # organisation = OrganisationShortSerializer()
    # manager = EmployeeShortSerializer()

    class Meta:
        model = Group
        fields = ("id", "name", "organisation", "manager")
