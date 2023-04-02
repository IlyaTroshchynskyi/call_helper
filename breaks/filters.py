import django_filters
from django.db.models import Q
from django.utils.datetime_safe import datetime

from breaks.models.organisations import Replacement


class ReplacementFilter(django_filters.FilterSet):
    CATEGORY_CHOICES = (
        ("active", "Active"),
        ("future", "Future"),
        ("archive", "Archive"),
    )

    category = django_filters.ChoiceFilter(
        method="category_filter",
        choices=CATEGORY_CHOICES,
        label="category",
    )

    class Meta:
        model = Replacement
        fields = ("group",)

    def category_filter(self, queryset, name, value):
        now = datetime.now().date()
        filters = {
            "active": Q(date=now),
            "future": Q(date__gt=now),
            "archive": Q(date__lt=now),
        }
        if value not in filters:
            return queryset

        return queryset.filter(filters[value])
