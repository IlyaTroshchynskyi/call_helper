# Generated by Django 4.1 on 2023-04-01 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("breaks", "0014_replacementmember_replacement_members_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="replacementmember",
            options={"verbose_name": "Change - group member", "verbose_name_plural": "Changes - group members"},
        ),
        migrations.RemoveField(
            model_name="break",
            name="employee",
        ),
        migrations.AddField(
            model_name="break",
            name="member",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="breaks",
                to="breaks.replacementmember",
                verbose_name="Shift member",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="replacementmember",
            name="status",
            field=models.ForeignKey(
                blank=True,
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="members",
                to="breaks.replacementstatus",
                verbose_name="Status",
            ),
        ),
        migrations.AlterField(
            model_name="replacementmember",
            name="time_break_end",
            field=models.DateTimeField(blank=True, editable=False, null=True, verbose_name="Came back from lunch"),
        ),
        migrations.AlterField(
            model_name="replacementmember",
            name="time_break_start",
            field=models.DateTimeField(blank=True, editable=False, null=True, verbose_name="Gone for lunch"),
        ),
        migrations.AlterField(
            model_name="replacementmember",
            name="time_offline",
            field=models.DateTimeField(blank=True, editable=False, null=True, verbose_name="Finished my shift"),
        ),
        migrations.AlterField(
            model_name="replacementmember",
            name="time_online",
            field=models.DateTimeField(blank=True, editable=False, null=True, verbose_name="Started shift"),
        ),
    ]
