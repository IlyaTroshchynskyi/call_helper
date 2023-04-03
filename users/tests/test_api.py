import json
from collections import OrderedDict

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


User = get_user_model()


class UsersApiTestCase(APITestCase):
    def setUp(self) -> None:
        test_data = {
            "username": "ilya",
            "first_name": "Test_Reg",
            "last_name": "Last",
            "email": "user@example.com",
            "password": "Strong12345",
        }

        self.user_1 = User.objects.create_user(**test_data)
        test_data["username"] = "Ilya1"
        test_data["email"] = "user1@example.com"
        test_data["is_corporate_account"] = True
        self.user_2 = User.objects.create_user(**test_data)
        test_data["username"] = "Search name"
        test_data["is_corporate_account"] = False
        self.user_3 = User.objects.create_user(**test_data)

    def test_registration_view(self):
        test_data = {
            "first_name": "Test_Reg",
            "last_name": "Last",
            "email": "userreg@example.com",
            "password": "Pass_12345",
        }

        json_data = json.dumps(test_data)
        response = self.client.post(reverse("api:reg"), data=json_data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual("Test_Reg", response.data.get("first_name"))
        self.assertEqual("Last", response.data.get("last_name"))
        self.assertTrue("userreg@example.com", response.data.get("email"))

    def test_change_password_view(self):
        self.client.force_login(self.user_1)
        test_data = {"old_password": "Strong12345", "new_password": "Strong123new"}

        json_data = json.dumps(test_data)
        response = self.client.post(reverse("api:change_passwd"), data=json_data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_me(self):
        self.client.force_login(self.user_1)
        response = self.client.get(reverse("api:me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user_1.id)
        self.assertEqual(response.data["first_name"], self.user_1.first_name)
        self.assertEqual(response.data["email"], self.user_1.email)
        self.assertEqual(response.data["last_name"], self.user_1.last_name)
        self.assertEqual(response.data["phone_number"], self.user_1.phone_number)
        self.assertEqual(response.data["username"], self.user_1.username)
        self.assertEqual(response.data["profile"], OrderedDict([("telegram_id", None)]))

    def test_post_me(self):
        data = {
            "first_name": "Updated",
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user_1)
        response = self.client.patch(reverse("api:me"), data=json_data, content_type="application/json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.user_1.refresh_from_db()
        self.assertEqual(self.user_1.first_name, "Updated")

    def test_post_raise_error_for_profile(self):
        data = {"first_name": "Updated_new", "profile": {"telegram_id": "1" * 21}}
        json_data = json.dumps(data)
        self.client.force_login(self.user_1)
        response = self.client.patch(reverse("api:me"), data=json_data, content_type="application/json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.user_1.refresh_from_db()
        self.assertEqual(self.user_1.first_name, "Test_Reg")
        self.assertEqual(
            response.data["profile"]["telegram_id"],
            [ErrorDetail(string="Ensure this field has no more than 20 characters.", code="max_length")],
        )

    def test_users_search_not_corporate_account(self):
        self.client.force_login(self.user_1)
        response = self.client.get("/api/users/search/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            response.data[0],
            OrderedDict(
                [
                    ("id", self.user_3.id),
                    ("username", "Search name"),
                    ("email", "user1@example.com"),
                    ("full_name", "Test_Reg Last"),
                ]
            ),
        )

    def test_users_search_by_name(self):
        self.client.force_login(self.user_1)
        response = self.client.get("/api/users/search/", {"search": "Search name"})
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            response.data[0],
            OrderedDict(
                [
                    ("id", self.user_3.id),
                    ("username", "Search name"),
                    ("email", "user1@example.com"),
                    ("full_name", "Test_Reg Last"),
                ]
            ),
        )
