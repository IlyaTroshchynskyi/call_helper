from django.contrib.auth import get_user_model
from django.db import models

from breaks.constants import BREAK_CREATED_STATUS, BREAK_CREATED_DEFAULT
from common.models import BaseDictModelMixin

User = get_user_model()


class GroupInfo(models.Model):
    group = models.OneToOneField(
        "organizations.Group",
        models.CASCADE,
        related_name="breaks_info",
        verbose_name="Group",
        primary_key=True,
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
        verbose_name = "Parameter Launch Break"
        verbose_name_plural = "Parameter Launch Break"

    def __str__(self):
        return f"{self.group}"


class Replacement(models.Model):
    group = models.ForeignKey(
        "breaks.GroupInfo", models.CASCADE, "replacements", verbose_name="Group"
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
