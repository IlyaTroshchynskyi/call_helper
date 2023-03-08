# Generated by Django 4.1 on 2023-03-06 19:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Name")),
                (
                    "director",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="organizations_directors",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Director",
                    ),
                ),
                (
                    "employees",
                    models.ManyToManyField(
                        blank=True,
                        related_name="organizations_employees",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Employees",
                    ),
                ),
            ],
            options={
                "verbose_name": "Organization",
                "verbose_name_plural": "Organizations",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Group",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Name")),
                (
                    "min_active",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="Min count active employees"
                    ),
                ),
                ("break_start", models.TimeField(blank=True, null=True, verbose_name="Start break")),
                ("break_end", models.TimeField(blank=True, null=True, verbose_name="End break")),
                (
                    "break_max_duration",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="Max duration of break"
                    ),
                ),
                (
                    "employees",
                    models.ManyToManyField(
                        blank=True,
                        related_name="groups_employees",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Employees",
                    ),
                ),
                (
                    "manager",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="groups_managers",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Manager",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="groups",
                        to="organizations.organization",
                        verbose_name="Organizations",
                    ),
                ),
            ],
            options={
                "verbose_name": "Group",
                "verbose_name_plural": "Groups",
                "ordering": ("name",),
            },
        ),
    ]
