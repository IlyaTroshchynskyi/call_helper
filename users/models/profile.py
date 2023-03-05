from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        "users.User",
        models.CASCADE,
        related_name="profile",
        verbose_name="Users",
        primary_key=True,
    )
    telegram_id = models.CharField("Telegram ID", max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Profile of User"
        verbose_name_plural = "Profiles of Users"

    def __str__(self):
        return f"{self.user} ({self.pk})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
