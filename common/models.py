import threading

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


User = get_user_model()


class BaseDictModelMixin(models.Model):
    code = models.CharField("Code", max_length=16, primary_key=True)
    name = models.CharField("Name", max_length=32)
    sort = models.PositiveSmallIntegerField("Sorting", null=True, blank=True)
    is_active = models.BooleanField("Activity Status", default=True)

    class Meta:
        ordering = ("sort",)
        abstract = True

    def __str__(self):
        return f"{self.code} ({self.name})"


class DateMixin(models.Model):
    created_at = models.DateTimeField("Created at", null=True, blank=False)
    updated_at = models.DateTimeField("Updated at", null=True, blank=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)


class InfoMixin(DateMixin):
    created_by = models.ForeignKey(
        User,
        models.SET_NULL,
        "created_%(app_label)s_%(class)s",
        verbose_name="Created by",
        null=True,
    )
    updated_by = models.ForeignKey(
        User,
        models.SET_NULL,
        "updated_%(app_label)s_%(class)s",
        verbose_name="Updated by",
        null=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # from crum import get_current_user
        request = threading.current_thread().request
        if request and hasattr(request, "user"):
            user = request.user
            print(user)
        # user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk:
            self.created_by = user
        self.updated_by = user
        super().save(*args, **kwargs)
