# core/hypertension/models.py

from django.db import models
from django.contrib.auth.models import User

# -----------------------------
# PROFILE MODEL (NEW)
# -----------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


# -----------------------------
# BLOOD PRESSURE MODEL (FIXED)
# -----------------------------
class BloodPressureReading(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="bp_readings",
        null=True,      # allow migration of old data
        blank=True
    )

    systolic = models.IntegerField()
    diastolic = models.IntegerField()
    pulse = models.PositiveIntegerField(null=True, blank=True)

    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.recorded_at:%Y-%m-%d %H:%M} {self.systolic}/{self.diastolic}"
