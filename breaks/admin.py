from django.contrib import admin

from breaks.models.organizations import Organization, Group


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
