from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} Profile"


class BloodPressureReading(models.Model):
    profile = models.ForeignKey(Profile, related_name='bp_readings', on_delete=models.CASCADE, null=True, blank=True)
    systolic = models.IntegerField()
    diastolic = models.IntegerField()
    pulse = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        ts = self.recorded_at.strftime("%Y-%m-%d %H:%M") if self.recorded_at else "unknown time"
        return f"{self.systolic}/{self.diastolic} @ {ts}"


# New WatchSync model (your provided code)
class WatchSync(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_connected = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)
    device_name = models.CharField(max_length=100, null=True, blank=True)
    battery_level = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Watch Sync"


# Model to store blood pressure readings reported from a paired watch
class WatchBloodPressure(models.Model):
    watch_sync = models.ForeignKey(WatchSync, related_name='watch_readings', on_delete=models.CASCADE)
    systolic = models.IntegerField()
    diastolic = models.IntegerField()
    pulse = models.PositiveIntegerField(null=True, blank=True)
    recorded_at = models.DateTimeField(default=timezone.now)
    raw = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        ts = self.recorded_at.strftime("%Y-%m-%d %H:%M") if self.recorded_at else "unknown time"
        return f"Watch {self.systolic}/{self.diastolic} @ {ts}"


# -----------------------------
# Sodium intake models
# -----------------------------
class Meal(models.Model):
    SOURCE_CHOICES = [
        ('manual', 'Manual'),
        ('spoon', 'Spoon'),
        ('import', 'Imported'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meals')
    name = models.CharField(max_length=200, blank=True)
    sodium_mg = models.PositiveIntegerField(help_text='Sodium in milligrams')
    portion = models.CharField(max_length=64, blank=True)
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES, default='manual')
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [models.Index(fields=['user', 'recorded_at'])]

    def __str__(self):
        return f'{self.name or "Meal"} {self.sodium_mg}mg @ {self.recorded_at.date()}'


class DailySummary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_summaries')
    date = models.DateField()
    total_mg = models.PositiveIntegerField(default=0)
    percent_of_limit = models.FloatField(default=0.0)
    highest_meal = models.ForeignKey(Meal, null=True, blank=True, on_delete=models.SET_NULL)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f'{self.user} {self.date} {self.total_mg}mg'


class Alert(models.Model):
    THRESHOLD_CHOICES = [
        ('50', '50%'),
        ('75', '75%'),
        ('100', '100%'),
        ('120', '120%'),
    ]
    SEVERITY = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sodium_alerts')
    date = models.DateField()
    threshold = models.CharField(max_length=8, choices=THRESHOLD_CHOICES)
    severity = models.CharField(max_length=8, choices=SEVERITY, default='info')
    message = models.CharField(max_length=400)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # Extended fields for API alerts
    sodium_total = models.PositiveIntegerField(null=True, blank=True)
    threshold_percent = models.FloatField(null=True, blank=True)
    device = models.ForeignKey('Device', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        indexes = [models.Index(fields=['user', 'date', 'threshold'])]
        ordering = ['-created_at']

    def __str__(self):
        return f'Alert {self.user} {self.date} {self.threshold}'


class WeeklyReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='weekly_reports')
    week_start = models.DateField(help_text='Monday of the week (ISO)')
    avg_daily_mg = models.FloatField()
    days_over_limit = models.PositiveSmallIntegerField()
    highest_day = models.DateField(null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'week_start')
        ordering = ['-week_start']

    def __str__(self):
        return f'WeeklyReport {self.user} {self.week_start}'


class Device(models.Model):
    """Represents a paired hardware device (salt-sensing spoon, watch, etc.)
    Devices authenticate using a token to post measurements on behalf of a user.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devices')
    name = models.CharField(max_length=150, blank=True)
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['token']), models.Index(fields=['user'])]

    def __str__(self):
        return f'Device {self.name or self.token[:8]} ({self.user})'
