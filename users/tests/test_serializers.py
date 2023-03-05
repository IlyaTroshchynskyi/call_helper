"""
    Collect all tests for serializers
"""
from collections import OrderedDict

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from users.serializers import RegistrationSerializer, MeUpdateSerializer

User = get_user_model()


class SerializersTestCase(APITestCase):
    """
    Class for testing serializers
    """

    def setUp(self):
        test_data = {
            "first_name": "Test_Reg",
            "last_name": "Last",
            "email": "user@example.com",
            "password": "Pass_12345",
        }
        self.user_1 = User.objects.create_user(**test_data)
        test_data["email"] = "user1@example.com"
        self.user_2 = User.objects.create_user(**test_data)

    def test_registration_serializer(self):
        result = RegistrationSerializer([self.user_1, self.user_2], many=True).data
        expected_data = [
            {
                "id": self.user_1.id,
                "first_name": "Test_Reg",
                "last_name": "Last",
                "email": "user@example.com",
            },
            {
                "id": self.user_2.id,
                "first_name": "Test_Reg",
                "last_name": "Last",
                "email": "user1@example.com",
            },
        ]
        self.assertEqual(expected_data, result)

    def test_me_update_serializer(self):
        result = MeUpdateSerializer([self.user_1], many=True).data
        expected_result = [
            OrderedDict(
                [
                    ("id", self.user_1.id),
                    ("first_name", "Test_Reg"),
                    ("last_name", "Last"),
                    ("email", "user@example.com"),
                    ("phone_number", None),
                    ("username", "user@example.com"),
                    ("profile", OrderedDict([("telegram_id", None)])),
                ]
            )
        ]
        self.assertEqual(expected_result, result)
