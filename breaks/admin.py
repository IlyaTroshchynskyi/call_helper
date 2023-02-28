from django.contrib import admin
from django.contrib.admin import TabularInline
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from breaks.models.organizations import (
    Organization,
    Group,
    Replacement,
    ReplacementStatus,
    ReplacementEmployee,
    BreakStatus,
    Break,
)


class ReplacementEmployeeInline(TabularInline):
    model = ReplacementEmployee
    fields = ("employee", "status")


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "director")
    filter_horizontal = ("employees",)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "manager", "min_active", "replacement_count")
    list_display_links = (
        "id",
        "name",
    )
    search_fields = ("name",)

    def replacement_count(self, obj):
        return obj.replacement_count

    def get_queryset(self, request):
        queryset = Group.objects.annotate(replacement_count=Count("replacements__id"))
        return queryset


@admin.register(Replacement)
class ReplacementAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "break_start", "break_end", "break_max_duration")
    inlines = (ReplacementEmployeeInline,)
    autocomplete_fields = ("group",)


@admin.register(ReplacementStatus)
class ReplacementStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "sort", "is_active")


@admin.register(BreakStatus)
class BreakStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "sort", "is_active")


@admin.register(Break)
class BreakAdmin(admin.ModelAdmin):
    list_display = ("id", "replacement_link", "break_start", "break_end", "status")
    list_filter = ("status",)
    empty_value_display = "Unknown"
    radio_fields = {"status": admin.VERTICAL}

    def replacement_link(self, obj):
        link = reverse("admin:breaks_replacement_change", args=[obj.replacement.id])
        return format_html('<a href="{}">{}</a>', link, obj.replacement)
