from rest_framework import serializers
from .models import Meal, DailySummary, Alert, WeeklyReport


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'name', 'sodium_mg', 'portion', 'source', 'recorded_at']
        extra_kwargs = {
            'sodium_mg': {'label': 'Sodium (mg)'},
            'recorded_at': {'label': 'Time'},
        }


class DailySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySummary
        fields = ['date', 'total_mg', 'percent_of_limit', 'highest_meal']


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'date', 'threshold', 'severity', 'message', 'created_at', 'is_read']


class WeeklyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyReport
        fields = ['week_start', 'avg_daily_mg', 'days_over_limit', 'highest_day', 'generated_at']
