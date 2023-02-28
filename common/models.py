from django.db import models


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
