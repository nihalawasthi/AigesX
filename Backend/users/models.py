from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class CustomUser(AbstractUser):
    DISPLAY_LIGHT = "light"
    DISPLAY_DARK = "dark"

    DISPLAY_MODE_CHOICES = [
        (DISPLAY_LIGHT, "Light"),
        (DISPLAY_DARK, "Dark"),
    ]

    LANGUAGE_EN = "en"
    LANGUAGE_ES = "es"
    LANGUAGE_FR = "fr"
    LANGUAGE_DE = "de"
    LANGUAGE_HI = "hi"

    LANGUAGE_CHOICES = [
        (LANGUAGE_EN, "English"),
        (LANGUAGE_ES, "Spanish"),
        (LANGUAGE_FR, "French"),
        (LANGUAGE_DE, "German"),
        (LANGUAGE_HI, "Hindi"),
    ]

    profile_picture = models.TextField(blank=True, default="")
    display_mode = models.CharField(max_length=16, choices=DISPLAY_MODE_CHOICES, default=DISPLAY_LIGHT)
    preferred_language = models.CharField(max_length=8, choices=LANGUAGE_CHOICES, default=LANGUAGE_EN)
    notify_job_complete = models.BooleanField(default=True)
    notify_critical_only = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    session_alerts = models.BooleanField(default=True)
    default_timeout_seconds = models.PositiveIntegerField(default=300)
    default_memory_limit_mb = models.PositiveIntegerField(default=512)

    groups = models.ManyToManyField(Group, related_name="customuser_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_set", blank=True)
