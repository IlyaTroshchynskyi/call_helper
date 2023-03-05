from django.contrib.auth import get_user_model
from django.db import models

from breaks.constants import BREAK_CREATED_STATUS, BREAK_CREATED_DEFAULT
from common.models import BaseDictModelMixin

User = get_user_model()


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
    manager = models.ForeignKey(User, models.RESTRICT, "group_managers", verbose_name="Manager")
    employees = models.ManyToManyField(User, "group_employees", verbose_name="Employees", blank=True)
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

    def __str__(self):
        return f"{self.name}"


class Replacement(models.Model):
    group = models.ForeignKey(Group, models.CASCADE, "replacements", verbose_name="Group")
    date = models.DateField("Date of replacement")
    break_start = models.TimeField("Start break")
    break_end = models.TimeField("End break")
    break_max_duration = models.PositiveSmallIntegerField("Max time of duration break")

    class Meta:
        verbose_name = "Replacement"
        verbose_name_plural = "Replacements"
        ordering = ("-date",)

    def __str__(self):
        return f"Replacement №{self.pk} for {self.group}"


class ReplacementStatus(BaseDictModelMixin):
    class Meta:
        verbose_name = "Replacement Status"
        verbose_name_plural = "Replacements Status"


class BreakStatus(BaseDictModelMixin):
    class Meta:
        verbose_name = "Break Status"
        verbose_name_plural = "Breaks Status"


class ReplacementEmployee(models.Model):
    employee = models.ForeignKey(User, models.CASCADE, "replacements", verbose_name="Employees")
    replacement = models.ForeignKey(
        Replacement, models.CASCADE, "employees", verbose_name="Replacement"
    )
    status = models.ForeignKey(
        ReplacementStatus,
        models.CASCADE,
        "replacement_employees",
        verbose_name="Status",
    )

    class Meta:
        verbose_name = "Replacement - Employees"
        verbose_name_plural = "Replacements - Employees"

    def __str__(self):
        return f"Replacement {self.replacement} for {self.employee}"


class Break(models.Model):
    replacement = models.ForeignKey(
        Replacement, models.CASCADE, "breaks", verbose_name="Replacement"
    )
    employee = models.ForeignKey(User, models.CASCADE, "breaks", verbose_name="Employees")
    break_start = models.TimeField("Start break", null=True, blank=True)
    break_end = models.TimeField("End break", null=True, blank=True)
    status = models.ForeignKey(
        BreakStatus, models.RESTRICT, "breaks", verbose_name="Status", blank=True
    )

    class Meta:
        verbose_name = "Lunch break"
        verbose_name_plural = "Lunch breaks"
        ordering = ("-replacement__date", "break_start")

    def __str__(self):
        return f"Break of user{ self.employee} ({self.pk})"

    def save(self, *args, **kwargs):
        if not self.pk:
            status, created = BreakStatus.objects.get_or_create(
                code=BREAK_CREATED_STATUS, defaults=BREAK_CREATED_DEFAULT
            )
            self.status = status
        return super().save(*args, **kwargs)
