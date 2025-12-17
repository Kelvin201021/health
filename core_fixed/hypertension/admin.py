from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import WatchSync, Profile, BloodPressureReading

# Inline BP readings under Profile
class BloodPressureInline(admin.TabularInline):
    model = BloodPressureReading
    extra = 0
    fields = ('systolic', 'diastolic', 'pulse', 'recorded_at')
    readonly_fields = ('recorded_at',)
    ordering = ('-recorded_at',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)
    inlines = (BloodPressureInline,)

@admin.register(WatchSync)
class WatchSyncAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_connected', 'device_name', 'battery_level', 'last_synced')
    list_filter = ('is_connected',)
    search_fields = ('user__username', 'device_name')
    readonly_fields = ('last_synced',)
    ordering = ('-last_synced',)

# Export action for BP readings
def export_bp_csv(modeladmin, request, queryset):
    """
    Export selected BloodPressureReading rows as CSV.
    """
    meta = modeladmin.model._meta
    field_names = ['profile__user__username', 'systolic', 'diastolic', 'pulse', 'notes', 'recorded_at']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=blood_pressure_readings.csv'
    writer = csv.writer(response)

    # header
    writer.writerow(['username', 'systolic', 'diastolic', 'pulse', 'notes', 'recorded_at'])

    for obj in queryset:
        username = obj.profile.user.username if obj.profile and obj.profile.user else ''
        writer.writerow([
            username,
            obj.systolic,
            obj.diastolic,
            obj.pulse or '',
            obj.notes or '',
            obj.recorded_at.isoformat() if obj.recorded_at else ''
        ])

    return response
export_bp_csv.short_description = "Export selected readings as CSV"

@admin.register(BloodPressureReading)
class BloodPressureReadingAdmin(admin.ModelAdmin):
    list_display = ('profile', 'systolic', 'diastolic', 'pulse', 'recorded_at')
    list_filter = ('recorded_at',)
    search_fields = ('profile__user__username',)
    date_hierarchy = 'recorded_at'
    actions = [export_bp_csv]
    readonly_fields = ('recorded_at',)
