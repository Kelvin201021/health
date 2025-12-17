from datetime import datetime
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from .models import Meal, DailySummary, Alert, WeeklyReport

DAILY_LIMIT_MG = getattr(settings, 'SODIUM_DAILY_LIMIT_MG', 2000)

THRESHOLDS = [
    ('50', int(0.50 * DAILY_LIMIT_MG), 'info'),
    ('75', int(0.75 * DAILY_LIMIT_MG), 'warning'),
    ('100', DAILY_LIMIT_MG, 'danger'),
    ('120', int(1.20 * DAILY_LIMIT_MG), 'danger'),
]

ALERT_MESSAGES = {
    '50': 'You have consumed half of the recommended daily sodium.',
    '75': 'You are at 75% of the daily sodium limit — consider lowering salt intake for remaining meals.',
    '100': 'You have reached the recommended daily sodium limit. Try to avoid salty foods for the rest of the day.',
    '120': 'You have exceeded the recommended limit — consider seeking medical advice if you feel unwell.',
}


def _get_date(dt):
    return dt.date()


@transaction.atomic
def add_meal_and_update(user, name, sodium_mg, recorded_at=None, portion='', source='manual'):
    if recorded_at is None:
        recorded_at = timezone.now()
    meal = Meal.objects.create(
        user=user,
        name=name or '',
        sodium_mg=int(max(0, int(sodium_mg))),
        portion=portion or '',
        source=source,
        recorded_at=recorded_at,
    )
    day = _get_date(recorded_at)
    _recompute_daily_summary(user, day)
    return meal


def _recompute_daily_summary(user, day_date):
    from django.db.models import Sum
    tz = timezone.get_current_timezone()
    start = timezone.datetime.combine(day_date, timezone.datetime.min.time()).replace(tzinfo=tz)
    end = timezone.datetime.combine(day_date, timezone.datetime.max.time()).replace(tzinfo=tz)
    meals = Meal.objects.filter(user=user, recorded_at__range=(start, end))
    total_mg = meals.aggregate(total=Sum('sodium_mg'))['total'] or 0

    percent = (total_mg / DAILY_LIMIT_MG) * 100 if DAILY_LIMIT_MG else 0

    highest = meals.order_by('-sodium_mg').first()

    summary, created = DailySummary.objects.update_or_create(
        user=user, date=day_date,
        defaults={
            'total_mg': int(total_mg),
            'percent_of_limit': round(percent, 1),
            'highest_meal': highest,
        }
    )

    _create_threshold_alerts(user, day_date, total_mg)
    return summary


def _create_threshold_alerts(user, day_date, total_mg):
    for code, value, severity in THRESHOLDS:
        if total_mg >= value:
            exists = Alert.objects.filter(user=user, date=day_date, threshold=code).exists()
            if not exists:
                Alert.objects.create(
                    user=user,
                    date=day_date,
                    threshold=code,
                    severity=severity,
                    message=ALERT_MESSAGES.get(code, ''),
                )


def get_daily_summary_and_advice(user, day_date):
    try:
        summary = DailySummary.objects.get(user=user, date=day_date)
    except DailySummary.DoesNotExist:
        summary = None

    advice = ''
    if summary:
        pct = summary.percent_of_limit
        if pct >= 120:
            advice = 'You have exceeded recommended sodium intake. Rest, hydrate, and consider contacting your clinician if symptomatic.'
        elif pct >= 100:
            advice = 'You reached today\'s sodium limit — avoid salty foods for the remainder of the day.'
        elif pct >= 75:
            advice = 'You are above 75% of the daily limit — reduce salt in next meals.'
        elif pct >= 50:
            advice = 'You reached half of the daily limit — aim for low-sodium choices now.'
        else:
            advice = 'You are within safe limits — keep choosing low-sodium options.'
    else:
        advice = 'No meals recorded today. Add a meal or take a spoon reading.'

    return summary, advice
