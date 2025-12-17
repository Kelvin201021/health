import json
from datetime import timedelta

from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings

from .sodium_services import add_meal_and_update, get_daily_summary_and_advice
from .models import DailySummary, Alert, Device


@csrf_exempt
@require_POST
def api_add_meal(request):
    # Allow device token auth via `Authorization: Token <token>` or `X-Device-Token` header.
    data = json.loads(request.body.decode('utf-8'))
    device = None
    token = None
    auth_hdr = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_hdr:
        if auth_hdr.lower().startswith('token '):
            token = auth_hdr.split(None, 1)[1].strip()
        else:
            token = auth_hdr.strip()
    if not token:
        token = request.META.get('HTTP_X_DEVICE_TOKEN')
    if token:
        try:
            device = Device.objects.get(token=token)
            device.last_seen = timezone.now()
            device.save(update_fields=['last_seen'])
        except Device.DoesNotExist:
            device = None

    # Determine user (device -> device.user, else session user)
    if device:
        user_obj = device.user
    else:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        user_obj = request.user

    name = data.get('name', '')
    sodium_mg = int(data.get('sodium_mg', 0))
    recorded_at = data.get('recorded_at')
    if recorded_at:
        from django.utils.dateparse import parse_datetime
        recorded_at = parse_datetime(recorded_at)
        if recorded_at is None:
            recorded_at = timezone.now()
    else:
        recorded_at = timezone.now()

    source = 'spoon' if device else 'manual'
    meal = add_meal_and_update(user_obj, name=name, sodium_mg=sodium_mg, recorded_at=recorded_at, source=source)
    day = recorded_at.date()
    summary, advice = get_daily_summary_and_advice(user_obj, day)
    # Determine alert level/message based on cumulative daily sodium thresholds
    alert_level = None
    alert_message = None
    if summary:
        pct = summary.percent_of_limit
        if pct >= 120:
            alert_level = 'danger'
            alert_message = 'Sodium intake is above 120% of your daily limit — high risk.'
            threshold_value = 120
        elif pct >= 100:
            alert_level = 'danger'
            alert_message = 'You have reached or exceeded your daily sodium limit.'
            threshold_value = 100
        elif pct >= 75:
            alert_level = 'warning'
            alert_message = 'You have reached 75% of your daily sodium limit — consider reducing intake.'
            threshold_value = 75
        elif pct >= 50:
            alert_level = 'info'
            alert_message = 'You have reached 50% of your daily sodium limit.'
            threshold_value = 50
        else:
            threshold_value = None

    # Persist an Alert row when thresholds are crossed
    try:
        if alert_level and alert_message:
            # Deduplicate: one alert per device per day per alert_level.
            # If an alert for the same device/day/level exists, update it.
            # If threshold increases (e.g., info -> warning -> danger), update an existing lower-severity alert.
            severity_order = {'info': 1, 'warning': 2, 'danger': 3}
            new_weight = severity_order.get(alert_level, 0)

            existing_exact = Alert.objects.filter(user=user_obj, device=device if device else None, date=day, severity=alert_level).first()
            if existing_exact:
                existing_exact.message = alert_message
                existing_exact.sodium_total = summary.total_mg if summary else None
                existing_exact.threshold_percent = summary.percent_of_limit if summary else None
                existing_exact.threshold = str(int(threshold_value)) if threshold_value else existing_exact.threshold
                existing_exact.save(update_fields=['message', 'sodium_total', 'threshold_percent', 'threshold'])
            else:
                # Look for any alert for same user/device/day with lower severity to upgrade
                candidate = None
                for a in Alert.objects.filter(user=user_obj, device=device if device else None, date=day):
                    w = severity_order.get(a.severity, 0)
                    if w < new_weight:
                        if candidate is None or w > severity_order.get(candidate.severity, 0):
                            candidate = a
                if candidate:
                    candidate.severity = alert_level
                    candidate.message = alert_message
                    candidate.sodium_total = summary.total_mg if summary else None
                    candidate.threshold_percent = summary.percent_of_limit if summary else None
                    candidate.threshold = str(int(threshold_value)) if threshold_value else candidate.threshold
                    candidate.save(update_fields=['severity', 'message', 'sodium_total', 'threshold_percent', 'threshold'])
                else:
                    Alert.objects.create(
                        user=user_obj,
                        date=day,
                        threshold=str(int(threshold_value)) if threshold_value else '',
                        severity=alert_level,
                        message=alert_message,
                        sodium_total=summary.total_mg if summary else None,
                        threshold_percent=summary.percent_of_limit if summary else None,
                        device=device if device else None,
                    )
    except Exception:
        # Don't fail the API if alert persistence has problems
        pass

    return JsonResponse({
        'meal_id': meal.id,
        'summary': {
            'date': str(summary.date),
            'total_mg': summary.total_mg,
            'percent_of_limit': summary.percent_of_limit,
        } if summary else None,
        'advice': advice,
        'alert_level': alert_level,
        'alert_message': alert_message,
    })


@login_required
@require_GET
def api_today_summary(request):
    today = timezone.localdate()
    summary, advice = get_daily_summary_and_advice(request.user, today)
    unread_alerts = list(request.user.sodium_alerts.filter(date=today, is_read=False).values('threshold','message','severity','created_at'))
    return JsonResponse({
        'summary': {
            'date': str(summary.date),
            'total_mg': summary.total_mg,
            'percent_of_limit': summary.percent_of_limit,
        } if summary else None,
        'advice': advice,
        'alerts': unread_alerts,
    })


@login_required
@require_GET
def api_weekly_summary(request):
    # last 7 days ending today
    today = timezone.localdate()
    start = today - timedelta(days=6)
    summaries = DailySummary.objects.filter(user=request.user, date__range=(start, today)).order_by('date')
    # basic aggregates
    total_days = summaries.count()
    avg = float(sum(s.total_mg for s in summaries) / total_days) if total_days else 0.0
    daily_limit = getattr(settings, 'SODIUM_DAILY_LIMIT_MG', 2000)
    days_over = sum(1 for s in summaries if s.total_mg >= daily_limit)
    daily_summaries = [
        {
            'date': str(s.date),
            'total_mg': s.total_mg,
            'percent_of_limit': s.percent_of_limit,
        }
        for s in summaries
    ]
    return JsonResponse({
        'week_start': str(start),
        'week_end': str(today),
        'avg_daily_mg': round(avg, 1),
        'days_over_limit': days_over,
        'daily_summaries': daily_summaries,
    })


@login_required
@require_GET
def api_get_alerts(request):
    # return recent alerts (unread first)
    alerts_qs = Alert.objects.filter(user=request.user).order_by('-created_at')[:50]
    alerts = [
        {
            'id': a.id,
            'date': str(a.date),
            'threshold': a.threshold,
            'severity': a.severity,
            'message': a.message,
            'created_at': a.created_at.isoformat() if a.created_at else None,
            'is_read': a.is_read,
        }
        for a in alerts_qs
    ]
    return JsonResponse({'alerts': alerts})
