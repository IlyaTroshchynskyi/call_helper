from common.serializers import ExtendedModelSerializer
from organizations.models import Employee
from organizations.serializers.nested.dicts import PositionShortSerializer
from users.serializers import UserShortSerializer


class EmployeeShortSerializer(ExtendedModelSerializer):
    user = UserShortSerializer()
    position = PositionShortSerializer()

    class Meta:
        fields = ("id", "user", "position")
        model = Employee
