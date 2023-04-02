from common.serializers import ExtendedModelSerializer
from organisations.models import Employee
from organisations.serializers.nested.dicts import PositionShortSerializer
from users.serializers import UserShortSerializer


class EmployeeShortSerializer(ExtendedModelSerializer):
    user = UserShortSerializer()
    position = PositionShortSerializer()

    class Meta:
        fields = ("id", "user", "position")
        model = Employee
