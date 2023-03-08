from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

from users.managers import CustomUserManager
from users.models.profile import Profile


class User(AbstractUser):
    phone_number = PhoneNumberField("Phone", unique=True, null=True)
    is_corporate_account = models.BooleanField("Corporate account", default=False)

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} ({self.pk})"


@receiver(post_save, sender=User)
def post_save_user(sender, instance, created, **kwargs):
    if not hasattr(instance, "profile"):
        Profile.objects.create(user=instance)
