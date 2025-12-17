import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_fixed.settings')
django.setup()

from django.contrib.auth import get_user_model
from hypertension.sodium_services import add_meal_and_update, get_daily_summary_and_advice
from hypertension.models import Alert

User = get_user_model()

# Try to find a real user: prefer superuser, then any user, else create testuser
user = User.objects.filter(is_superuser=True).first()
if not user:
    user = User.objects.first()
if not user:
    print('No users found — creating testuser with password TestPass123')
    user = User.objects.create_user('testuser', 'test@example.com', 'TestPass123')

print('Using user:', user.username)

# Add a sample meal
meal = add_meal_and_update(user, name='Automated Test Meal', sodium_mg=650, recorded_at=timezone.now(), source='manual')
print('Created meal id:', meal.id, 'sodium_mg:', meal.sodium_mg)

# Fetch today's summary and advice
today = timezone.localdate()
summary, advice = get_daily_summary_and_advice(user, today)
if summary:
    print('Daily total mg:', summary.total_mg)
    print('Percent of limit:', summary.percent_of_limit)
else:
    print('No summary found')

print('Advice:', advice)

# Print alerts for today
alerts = Alert.objects.filter(user=user, date=today)
print('Alerts for today:', alerts.count())
for a in alerts:
    print('-', a.threshold, a.severity, a.message)
