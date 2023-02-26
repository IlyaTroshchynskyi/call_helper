from django.contrib import admin
from django.contrib.admin import TabularInline

from breaks.models.organizations import (
    Organization,
    Group,
    Replacement,
    ReplacementStatus,
    ReplacementEmployee,
)


class ReplacementEmployeeInline(TabularInline):
    model = ReplacementEmployee
    fields = ("employee", "status")


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "director",
    )


@admin.register(Group)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "manager", "min_active")


@admin.register(Replacement)
class ReplacementAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "break_start", "break_end", "break_max_duration")
    inlines = (ReplacementEmployeeInline,)


@admin.register(ReplacementStatus)
class ReplacementStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "sort", "is_active")
