from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from users.serializers import (
    RegistrationSerializer,
    ChangePasswordSerializer,
    MeSerializer,
    MeUpdateSerializer,
)

User = get_user_model()


@extend_schema_view(
    post=extend_schema(summary="Registration of user", tags=["Authentication and Authorization"])
)
class RegistrationView(CreateAPIView):
    queryset = User.objects
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer


@extend_schema_view(
    post=extend_schema(
        # should be defined only for APIView because view don't know something about serializer
        request=ChangePasswordSerializer(),
        summary="Change password",
        tags=["Authentication and Authorization"],
    )
)
class ChangePasswordView(APIView):
    def post(self, request):
        user = request.user
        print("print user-----------", user)
        serializer = ChangePasswordSerializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(summary="Profile of users", tags=["Users"]),
    put=extend_schema(summary="Change the profile of users", tags=["Users"]),
    patch=extend_schema(summary="Change the profile of user partially", tags=["Users"]),
)
class MeView(RetrieveUpdateAPIView):
    # permission_classes = [IsNotCorporate]
    queryset = User.objects.all()
    serializer_class = MeSerializer
    http_method_names = ("get", "patch")

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return MeUpdateSerializer
        return MeSerializer

    def get_object(self):
        return self.request.user


# @extend_schema_view(
#     list=extend_schema(summary="Список пользователей Search", tags=["Словари"]),
# )
# class UserListSearchView(ListViewSet):
#     queryset = User.objects.exclude(Q(is_superuser=True) | Q(is_corporate_account=True))
#     serializer_class = UserSearchListSerializer
