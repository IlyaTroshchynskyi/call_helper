from django.contrib.auth.models import User
from django.db import models


class Organization(models.Model):
    name = models.CharField("Name", max_length=255)
    director = models.ForeignKey(
        User,
        models.RESTRICT,
        related_name="organization_directors",
        verbose_name="Director",
    )
    employees = models.ManyToManyField(
        User, "organization_employees", verbose_name="Employees", blank=True
    )

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.pk})"


class Group(models.Model):
    organization = models.ForeignKey(
        Organization, models.CASCADE, "groups", verbose_name="Organizations"
    )
    name = models.CharField("Name", max_length=255)
    manager = models.ForeignKey(
        User, models.RESTRICT, "group_managers", verbose_name="Manager"
    )
    employees = models.ManyToManyField(
        User, "group_employees", verbose_name="Employees", blank=True
    )
    min_active = models.PositiveSmallIntegerField(
        "Min count active employees", null=True, blank=True
    )
    break_start = models.TimeField("Start break", null=True, blank=True)
    break_end = models.TimeField("End break", null=True, blank=True)
    break_max_duration = models.PositiveSmallIntegerField(
        "Max duration of break", null=True, blank=True
    )

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"
        ordering = ("name",)
