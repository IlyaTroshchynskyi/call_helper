from django.utils import timezone

from django.contrib.auth import get_user_model
from django.db import models

from common.models import BaseDictModelMixin, InfoMixin
from organizations.constants import DIRECTOR_POSITION

User = get_user_model()


class Organization(InfoMixin):
    name = models.CharField("Name", max_length=255)
    director = models.ForeignKey(
        User,
        models.RESTRICT,
        related_name="organizations_directors",
        verbose_name="Director",
    )
    employees = models.ManyToManyField(
        User, "organizations_employees", verbose_name="Employees", blank=True, through="Employee"
    )

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.pk})"

    @property
    def director_employee(self):
        obj, create = self.employees_info.get_or_create(
            position_id=DIRECTOR_POSITION, defaults={"user": self.director}
        )
        return obj


class Group(InfoMixin):
    organization = models.ForeignKey(
        Organization, models.CASCADE, "groups", verbose_name="Organizations"
    )
    name = models.CharField("Name", max_length=255)
    manager = models.ForeignKey(User, models.RESTRICT, "groups_managers", verbose_name="Manager")
    members = models.ManyToManyField(
        "Employee",
        related_name="groups_members",
        verbose_name="Band members",
        blank=True,
        through="Member",
    )

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name}"


class Position(BaseDictModelMixin):
    class Meta:
        verbose_name = "Position"
        verbose_name_plural = "Positions"


class Employee(models.Model):
    organisation = models.ForeignKey("Organization", models.CASCADE, "employees_info")
    user = models.ForeignKey(User, models.CASCADE, "organisations_info")
    position = models.ForeignKey("Position", models.RESTRICT, "employees")
    date_joined = models.DateField("Date joined", default=timezone.now)

    class Meta:
        verbose_name = "Employee organization"
        verbose_name_plural = "Employee organizations"
        ordering = ("-date_joined",)
        unique_together = (("organisation", "user"),)

    def __str__(self):
        return f"Employee #{self.pk} {self.user}"

    # @property
    # def is_director(self):
    #     if self.position_id == DIRECTOR_POSITION:
    #         return True
    #     return False
    #
    # @property
    # def is_manager(self):
    #     if self.position_id == MANAGER_POSITION:
    #         return True
    #     return False
    #
    # @property
    # def is_operator(self):
    #     if self.position_id == OPERATOR_POSITION:
    #         return True
    #     return False


class Member(models.Model):
    group = models.ForeignKey(Group, models.CASCADE, "members_info")
    employee = models.ForeignKey(Employee, models.CASCADE, "groups_info")
    date_joined = models.DateField("Date joined", default=timezone.now)

    class Meta:
        verbose_name = "Band member"
        verbose_name_plural = "Band members"
        ordering = ("-date_joined",)
        unique_together = (("group", "employee"),)

    def __str__(self):
        return f"Employee {self.employee}"


class Offer(InfoMixin):
    organisation = models.ForeignKey(
        "Organization", models.RESTRICT, "offers", verbose_name="Organisation"
    )
    org_accept = models.BooleanField("Organization Consent", null=True, blank=True)
    user = models.ForeignKey(User, models.RESTRICT, "offers", verbose_name="User")
    user_accept = models.BooleanField("User Consent", null=True, blank=True)

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        ordering = ("-created_at",)
        unique_together = (("organisation", "user"),)

    def __str__(self):
        return f"Offer №{self.pk}"

    @property
    def is_from_org(self):
        """
        Is offer from organisation
        """
        return bool(self.user != self.created_by)

    @property
    def is_from_user(self):
        """
        Is offer from user
        """
        return bool(self.user == self.created_by)
