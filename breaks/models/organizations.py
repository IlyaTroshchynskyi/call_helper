from datetime import datetime, timedelta
from time import timezone

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Subquery, OuterRef, ExpressionWrapper, F, DateTimeField, Count, Q
from model_utils import FieldTracker
from django_generate_series.models import generate_series


from breaks.constants import (
    BREAK_CREATED_STATUS,
    BREAK_CREATED_DEFAULT,
    REPLACEMENT_MEMBER_OFFLINE,
    REPLACEMENT_MEMBER_ONLINE,
    REPLACEMENT_MEMBER_BREAK,
)
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
    min_active = models.PositiveSmallIntegerField("Min count active employees", null=True, blank=True)
    break_start = models.TimeField("Start break", null=True, blank=True)
    break_end = models.TimeField("End break", null=True, blank=True)
    break_max_duration = models.PositiveSmallIntegerField("Max duration of break", null=True, blank=True)

    class Meta:
        verbose_name = "Parameter Launch Break"
        verbose_name_plural = "Parameter Launch Break"

    def __str__(self):
        return f"{self.group}"


class Replacement(models.Model):
    group = models.ForeignKey("breaks.GroupInfo", models.CASCADE, "replacements", verbose_name="Group")
    date = models.DateField("Date of replacement")
    break_start = models.TimeField("Start break")
    break_end = models.TimeField("End break")
    break_max_duration = models.PositiveSmallIntegerField("Max time of duration break")
    min_active = models.PositiveSmallIntegerField(
        "Min. number of active employees",
        null=True,
        blank=True,
    )

    members = models.ManyToManyField(
        "organizations.Member", related_name="replacements", verbose_name="Shift members", through="ReplacementMember"
    )

    class Meta:
        verbose_name = "Replacement"
        verbose_name_plural = "Replacements"
        ordering = ("-date",)

    def __str__(self):
        return f"Replacement №{self.pk} for {self.group}"

    def free_breaks_available(self, break_start, break_end, exclude_break_id=None):
        breaks_sub_qs = Subquery(
            Break.objects.filter(replacement=OuterRef("pk"))
            .exclude(pk=exclude_break_id)
            .annotate(
                start_datetime=ExpressionWrapper(OuterRef("date") + F("break_start"), output_field=DateTimeField()),
                end_datetime=ExpressionWrapper(OuterRef("date") + F("break_end"), output_field=DateTimeField()),
            )
            .filter(
                start_datetime__lte=OuterRef("timeline"),
                end_datetime__gt=OuterRef("timeline"),
            )
            .values("pk")
        )

        replacement_sub_qs = (
            self.__class__.objects.filter(pk=self.pk)
            .annotate(timeline=OuterRef("term"))
            .order_by()
            .values("timeline")
            .annotate(
                pk=F("pk"),
                breaks=Count("breaks", filter=Q(breaks__id__in=breaks_sub_qs), distinct=True),
                members_count=Count("members", distinct=True),
                free_breaks=F("members_count") - F("breaks"),
            )
        )
        start_datetime = datetime.combine(self.date, break_start)
        end_datetime = datetime.combine(self.date, break_end) - timedelta(minutes=15)
        data_seq_qs = (
            generate_series(start_datetime, end_datetime, "15 minutes", output_field=DateTimeField)
            .annotate(
                breaks=Subquery(replacement_sub_qs.values("free_breaks")),
            )
            .order_by("breaks")
        )
        return data_seq_qs.first().breaks

    def get_member_by_user(self, user):
        return self.members_info.filter(member__employee__user=user).first()

    def get_break_for_user(self, user):
        return self.breaks.filter(member__member__employee__user=user).first()

    def get_break_status_for_user(self, user):
        member = self.get_member_by_user(user)
        break_obj = self.get_break_for_user(user)
        now = timezone.now().astimezone()
        if not member or self.date != now.date():
            return None
        if not break_obj:
            return "create"
        return "update"


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
    replacement = models.ForeignKey(Replacement, models.CASCADE, "employees", verbose_name="Replacement")
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
    member = models.ForeignKey("breaks.ReplacementMember", models.CASCADE, "breaks", verbose_name="Shift member")
    replacement = models.ForeignKey(Replacement, models.CASCADE, "breaks", verbose_name="Replacement")
    break_start = models.TimeField("Start break", null=True, blank=True)
    break_end = models.TimeField("End break", null=True, blank=True)
    status = models.ForeignKey(BreakStatus, models.RESTRICT, "breaks", verbose_name="Status", blank=True)

    class Meta:
        verbose_name = "Lunch break"
        verbose_name_plural = "Lunch breaks"
        ordering = ("-replacement__date", "break_start")

    def __str__(self):
        return f"Break of user{ self.member} ({self.pk})"

    def save(self, *args, **kwargs):
        if not self.pk:
            status, created = BreakStatus.objects.get_or_create(
                code=BREAK_CREATED_STATUS, defaults=BREAK_CREATED_DEFAULT
            )
            self.status = status
        return super().save(*args, **kwargs)


class ReplacementMember(models.Model):
    member = models.ForeignKey("organizations.Member", models.CASCADE, "replacements_info", verbose_name="Сотрудник")
    replacement = models.ForeignKey("breaks.Replacement", models.CASCADE, "members_info", verbose_name="Смена")
    status = models.ForeignKey(
        "breaks.ReplacementStatus", models.RESTRICT, "members", verbose_name="Status", blank=True
    )

    time_online = models.DateTimeField("Started shift", null=True, blank=True, editable=False)
    time_offline = models.DateTimeField("Finished my shift", null=True, blank=True, editable=False)
    time_break_start = models.DateTimeField("Gone for lunch", null=True, blank=True, editable=False)
    time_break_end = models.DateTimeField("Came back from lunch", null=True, blank=True, editable=False)
    tracker = FieldTracker()

    class Meta:
        verbose_name = "Change - group member"
        verbose_name_plural = "Changes - group members"

    def __str__(self):
        return f"Участник смены {self.member.employee.user.full_name} ({self.pk})"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.status_id = REPLACEMENT_MEMBER_OFFLINE
        else:
            if self.tracker.has_changed("status_id"):
                now = timezone.now()

                if self.status_id == REPLACEMENT_MEMBER_ONLINE:
                    if not self.time_online:
                        self.time_online = now
                    if self.time_break_start and not self.time_break_end:
                        self.time_break_end = now

                if self.status_id == REPLACEMENT_MEMBER_BREAK and not self.time_break_start:
                    self.time_break_start = now

                if self.status_id == REPLACEMENT_MEMBER_OFFLINE:
                    if not self.time_offline:
                        self.time_offline = now
                    if self.time_break_start and not self.time_break_end:
                        self.time_break_end = now
        super().save(*args, **kwargs)
