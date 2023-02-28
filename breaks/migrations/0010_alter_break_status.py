# Generated by Django 4.1 on 2023-02-28 18:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("breaks", "0009_remove_break_duration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="break",
            name="status",
            field=models.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="breaks",
                to="breaks.breakstatus",
                verbose_name="Status",
            ),
        ),
    ]
