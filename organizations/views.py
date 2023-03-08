from drf_spectacular.utils import extend_schema_view, extend_schema

from common.views import StatusListMixinView, ListViewSet, LCRUViewSet, LCRUDViewSet
from organizations.models import Position, Organization, Employee
from organizations.serializers import (
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
)


@extend_schema_view(
    list=extend_schema(summary="List of positions", tags=["Organization"]),
)
class PositionView(StatusListMixinView):
    queryset = Position.objects.all()


@extend_schema_view(
    list=extend_schema(summary="List organisations Search", tags=["Organization"]),
)
class OrganisationSearchView(ListViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganisationSearchListSerializer


@extend_schema_view(
    list=extend_schema(summary="List Organisations", tags=["Organization"]),
    retrieve=extend_schema(summary="Detail Organisation", tags=["Organization"]),
    create=extend_schema(summary="Create Organisation", tags=["Organization"]),
    update=extend_schema(summary="Change Organisation", tags=["Organization"]),
    partial_update=extend_schema(summary="Change organisation partially", tags=["Organization"]),
)
class OrganisationView(LCRUViewSet):
    # permission_classes = [IsMyOrganisation]
    queryset = Organization.objects.all()
    serializer_class = OrganisationListSerializer

    multi_serializer_class = {
        "list": OrganisationListSerializer,
        "retrieve": OrganisationRetrieveSerializer,
        "create": OrganisationCreateSerializer,
        "update": OrganisationUpdateSerializer,
        "partial_update": OrganisationUpdateSerializer,
    }

    http_method_names = ("get", "post", "patch")
    #
    #     filter_backends = (
    #         OrderingFilter,
    #         SearchFilter,
    #         DjangoFilterBackend,
    #         MyOrganisation,
    #     )
    #     filterset_class = OrganisationFilter
    #     ordering = ('name', 'id',)

    def get_serializer_class(self):
        return self.multi_serializer_class[self.action]


#     def get_queryset(self):
#         queryset = Organisation.objects.select_related(
#             'director',
#         ).prefetch_related(
#             'employees',
#             'groups',
#         ).annotate(
#             pax=Count('employees', distinct=True),
#             groups_count=Count('groups', distinct=True),
#             can_manage=Case(
#                 When(director=self.request.user, then=True),
#                 default=False,
#             )
#         )
#         return queryset


@extend_schema_view(
    list=extend_schema(summary="List employees of organisation", tags=["Organisation: Employee"]),
    retrieve=extend_schema(
        summary="Detail employee of organisation", tags=["Organisation: Employee"]
    ),
    create=extend_schema(summary="Create employee of organisation", tags=["Organisation: Employee"]),
    update=extend_schema(summary="Update employee of organisation", tags=["Organisation: Employee"]),
    partial_update=extend_schema(
        summary="Update employee of organisation partial", tags=["Organisation: Employee"]
    ),
    destroy=extend_schema(
        summary="Delete employee from organisation", tags=["Organisation: Employee"]
    ),
    search=extend_schema(
        filters=True,
        summary="List employees of organisation Search",
        tags=["Organisation: Employee"],
    ),
)
class EmployeeView(LCRUDViewSet):
    # permission_classes = [IsColleagues]

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
    http_method_names = (
        "get",
        "post",
        "patch",
        "delete",
    )

    def get_serializer_class(self):
        return self.multi_serializer_class[self.action]

    # filter_backends = (
    #     DjangoFilterBackend,
    #     OrderingFilter,
    #     SearchFilter,
    #     OwnedByOrganisation,
    # )
    # filterset_class = EmployeeFilter
    # ordering = ('position', 'date_joined', 'id',)
    #
    def get_queryset(self):
        qs = Employee.objects.select_related("user", "position").prefetch_related("organisation")
        return qs

    #
    # @action(methods=['GET'], detail=False, url_path='search')
    # def search(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)
    #
    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=dict())
    #     serializer.is_valid(raise_exception=True)
    #     return super().destroy(request, *args, **kwargs)
