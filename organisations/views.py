from django.db.models import Count, When, Case, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter

from common.views import StatusListMixinView, ListViewSet, LCRUViewSet, LCRUDViewSet, LCUViewSet, LCDViewSet
from organisations.backends import MyOrganisation, OwnedByOrganisation, MyGroup, OwnedByGroup
from organisations.factory import OfferFactory
from organisations.filters import (
    OrganisationFilter,
    EmployeeFilter,
    GroupFilter,
    OfferOrgFilter,
    OfferUserFilter,
)
from organisations.models import Position, Organisation, Employee, Group, Offer, Member
from organisations.permissions import IsMyOrganisation, IsColleagues, IsMyGroup, IsOfferManager
from organisations.serializers.api import (
    OrganisationSearchListSerializer,
    OrganisationListSerializer,
    OrganisationRetrieveSerializer,
    OrganisationCreateSerializer,
    OrganisationUpdateSerializer,
    EmployeeListSerializer,
    EmployeeRetrieveSerializer,
    EmployeeCreateSerializer,
    EmployeeUpdateSerializer,
    EmployeeSearchSerializer,
    EmployeeDeleteSerializer,
    GroupListSerializer,
    GroupRetrieveSerializer,
    GroupCreateSerializer,
    GroupUpdateSerializer,
    GroupSettingsUpdateSerializer,
    OfferOrgToUserListSerializer,
    OfferOrgToUserCreateSerializer,
    OfferOrgToUserUpdateSerializer,
    OfferUserToOrgListSerializer,
    OfferUserToOrgCreateSerializer,
    OfferUserToOrgUpdateSerializer,
    MemberListSerializer,
    MemberCreateSerializer,
    MemberSearchSerializer,
)


@extend_schema_view(list=extend_schema(summary="List of positions", tags=["Organisation"]))
class PositionView(StatusListMixinView):
    queryset = Position.objects.all()


@extend_schema_view(list=extend_schema(summary="List organisations Search", tags=["Organisation"]))
class OrganisationSearchView(ListViewSet):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSearchListSerializer


@extend_schema_view(
    list=extend_schema(summary="List Organisations", tags=["Organisation"]),
    retrieve=extend_schema(summary="Detail Organisation", tags=["Organisation"]),
    create=extend_schema(summary="Create Organisation", tags=["Organisation"]),
    update=extend_schema(summary="Change Organisation", tags=["Organisation"]),
    partial_update=extend_schema(summary="Change organisation partially", tags=["Organisation"]),
)
class OrganisationView(LCRUViewSet):
    permission_classes = [IsMyOrganisation]
    queryset = Organisation.objects.all()
    serializer_class = OrganisationListSerializer

    multi_serializer_class = {
        "list": OrganisationListSerializer,
        "retrieve": OrganisationRetrieveSerializer,
        "create": OrganisationCreateSerializer,
        "update": OrganisationUpdateSerializer,
        "partial_update": OrganisationUpdateSerializer,
    }

    http_method_names = ("get", "post", "patch")

    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend, MyOrganisation)
    filterset_class = OrganisationFilter
    ordering = ("name", "id")
    search_fields = ("name",)

    def get_queryset(self):
        queryset = (
            Organisation.objects.select_related("director")
            .prefetch_related("employees", "groups")
            .annotate(
                pax=Count("employees", distinct=True),
                groups_count=Count("groups", distinct=True),
                can_manage=Case(When(director=self.request.user, then=True), default=False),
            )
        )
        return queryset


@extend_schema_view(
    list=extend_schema(summary="List employees of organisation", tags=["Organisation: Employee"]),
    retrieve=extend_schema(summary="Detail employee of organisation", tags=["Organisation: Employee"]),
    create=extend_schema(summary="Create employee of organisation", tags=["Organisation: Employee"]),
    update=extend_schema(summary="Update employee of organisation", tags=["Organisation: Employee"]),
    partial_update=extend_schema(summary="Update employee of organisation partial", tags=["Organisation: Employee"]),
    destroy=extend_schema(summary="Delete employee from organisation", tags=["Organisation: Employee"]),
    search=extend_schema(
        filters=True, summary="List employees of organisation Search", tags=["Organisation: Employee"]
    ),
)
class EmployeeView(LCRUDViewSet):
    permission_classes = [IsColleagues]

    queryset = Employee.objects.all()
    serializer_class = EmployeeListSerializer

    multi_serializer_class = {
        "list": EmployeeListSerializer,
        "retrieve": EmployeeRetrieveSerializer,
        "create": EmployeeCreateSerializer,
        "update": EmployeeUpdateSerializer,
        "partial_update": EmployeeUpdateSerializer,
        "search": EmployeeSearchSerializer,
        "destroy": EmployeeDeleteSerializer,
    }

    lookup_url_kwarg = "employee_id"
    http_method_names = ("get", "post", "patch", "delete")

    def get_serializer_class(self):
        return self.multi_serializer_class[self.action]

    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter, OwnedByOrganisation)
    filterset_class = EmployeeFilter
    ordering = ("position", "date_joined", "id")

    def get_queryset(self):
        qs = Employee.objects.select_related("user", "position").prefetch_related("organisation")
        return qs

    @action(methods=["GET"], detail=False, url_path="search")
    def search(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=dict())
        serializer.is_valid(raise_exception=True)
        return super().destroy(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(summary="Group list", tags=["Organisations: Groups"]),
    retrieve=extend_schema(summary="Group detail", tags=["Organisations: Groups"]),
    create=extend_schema(summary="Создать группу", tags=["Organisations: Groups"]),
    update=extend_schema(summary="To create a group", tags=["Organisations: Groups"]),
    partial_update=extend_schema(summary="Change group partially", tags=["Organisations: Groups"]),
    update_settings=extend_schema(summary="Change group settings", tags=["Organisations: Groups"]),
)
class GroupView(LCRUViewSet):
    permission_classes = [IsMyGroup]

    queryset = Group.objects.all()
    serializer_class = GroupListSerializer

    multi_serializer_class = {
        "list": GroupListSerializer,
        "retrieve": GroupRetrieveSerializer,
        "create": GroupCreateSerializer,
        "update": GroupUpdateSerializer,
        "partial_update": GroupUpdateSerializer,
        "update_settings": GroupSettingsUpdateSerializer,
    }

    http_method_names = ("get", "post", "patch")

    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend, MyGroup)
    search_fields = ("name",)
    filterset_class = GroupFilter
    ordering = ("name", "id")

    def get_queryset(self):
        queryset = (
            Group.objects.select_related("manager")
            .prefetch_related("organisation", "organisation__director", "members")
            .annotate(
                pax=Count("members", distinct=True),
                can_manage=Case(
                    When(
                        Q(manager__user=self.request.user) | Q(organisation__director=self.request.user),
                        then=True,
                    ),
                    default=False,
                ),
                _is_member_count=Count(
                    "members",
                    filter=(Q(members__user=self.request.user)),
                    distinct=True,
                ),
                is_member=Case(
                    When(Q(_is_member_count__gt=0), then=True),
                    default=False,
                ),
            )
        )
        return queryset

    @action(methods=["PATCH"], detail=True, url_path="settings")
    def update_settings(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(summary="List offers of organisation", tags=["Organisation: Offers"]),
    create=extend_schema(summary="Create offer to user", tags=["Organisation: Offers"]),
    partial_update=extend_schema(summary="Change  user's offer partially", tags=["Organisation: Offers"]),
)
class OfferOrganisationView(LCUViewSet):
    permission_classes = [IsOfferManager]

    # docs can be wrong need to check
    queryset = Offer.objects.all()
    serializer_class = OfferOrgToUserListSerializer

    multi_serializer_class = {
        "list": OfferOrgToUserListSerializer,
        "create": OfferOrgToUserCreateSerializer,
        "partial_update": OfferOrgToUserUpdateSerializer,
    }

    lookup_url_kwarg = "offer_id"
    http_method_names = ("get", "post", "patch")

    filter_backends = (DjangoFilterBackend, OrderingFilter, OwnedByOrganisation)
    filterset_class = OfferOrgFilter
    ordering_fields = (
        "-created_at",
        "updated_at",
    )

    def get_queryset(self):
        return OfferFactory(self.request.user).org_list()


@extend_schema_view(
    list=extend_schema(summary="List offers of users", tags=["Organisation: Offers"]),
    create=extend_schema(summary="Create offer to organisation", tags=["Organisation: Offers"]),
    partial_update=extend_schema(summary="Change offer to organisation partially", tags=["Organisation: Offers"]),
)
class OfferUserView(LCUViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferUserToOrgListSerializer

    multi_serializer_class = {
        "list": OfferUserToOrgListSerializer,
        "create": OfferUserToOrgCreateSerializer,
        "partial_update": OfferUserToOrgUpdateSerializer,
    }

    http_method_names = ("get", "post", "patch")
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = OfferUserFilter
    ordering_fields = ("created_at", "updated_at")

    def get_queryset(self):
        return OfferFactory(self.request.user).user_list()


@extend_schema_view(
    list=extend_schema(summary="List of group members", tags=["Organisations: Groups: Members"]),
    create=extend_schema(summary="Create a group member", tags=["Organisations: Groups: Members"]),
    destroy=extend_schema(summary="Remove a member from a group", tags=["Organisations: Groups: Members"]),
    search=extend_schema(filters=True, summary="List of group members Search", tags=["Api"]),
)
class MemberView(LCDViewSet):
    permission_classes = [IsColleagues]

    queryset = Member.objects.all()
    serializer_class = MemberListSerializer

    multi_serializer_class = {
        "list": MemberListSerializer,
        "create": MemberCreateSerializer,
        "search": MemberSearchSerializer,
    }

    lookup_url_kwarg = "member_id"

    filter_backends = (OwnedByGroup,)

    def get_queryset(self):
        qs = Member.objects.select_related(
            "employee",
        ).prefetch_related(
            "group",
            "employee__user",
            "employee__organisation",
            "employee__organisation",
            "employee__position",
        )
        return qs

    @action(methods=["GET"], detail=False, url_path="search")
    def search(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
