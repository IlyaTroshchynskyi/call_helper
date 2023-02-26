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

    def __str__(self):
        return f"{self.name}"


class Replacement(models.Model):
    group = models.ForeignKey(
        Group, models.CASCADE, "replacements", verbose_name="Group"
    )
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


class ReplacementStatus(models.Model):
    code = models.CharField("Code", max_length=16, primary_key=True)
    name = models.CharField("Name", max_length=32)
    sort = models.PositiveSmallIntegerField("Sorting", null=True, blank=True)
    is_active = models.BooleanField("Activity Status", default=True)

    class Meta:
        verbose_name = "Replacement Status"
        verbose_name_plural = "Replacements Status"
        ordering = ("sort",)

    def __str__(self):
        return f"{self.code} for {self.name}"


class ReplacementEmployee(models.Model):
    employee = models.ForeignKey(
        User, models.CASCADE, "replacements", verbose_name="Employees"
    )
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
