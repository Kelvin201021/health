from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from ...models import Profile, BloodPressureReading, WatchSync, WatchBloodPressure

import random


class Command(BaseCommand):
    help = 'Create sample manual and watch blood pressure readings for a user'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to attach sample data to', required=True)

    def handle(self, *args, **options):
        username = options['username']
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'User "{username}" does not exist'))
            return

        profile, _ = Profile.objects.get_or_create(user=user)

        now = timezone.now()

        # create 8 manual readings spread over the last 8 days
        for i in range(8):
            ts = now - timezone.timedelta(days=8-i)
            s = random.randint(110, 150)
            d = random.randint(70, 95)
            BloodPressureReading.objects.create(profile=profile, systolic=s, diastolic=d, pulse=random.randint(60,85), recorded_at=ts)

        # ensure watch sync
        watchsync, _ = WatchSync.objects.get_or_create(user=user)
        watchsync.is_connected = True
        watchsync.last_synced = now
        watchsync.device_name = 'Hypertension SmartWatch'
        watchsync.battery_level = 88
        watchsync.save()

        # create 8 watch readings in last 8 days
        for i in range(8):
            ts = now - timezone.timedelta(days=8-i, hours=1)
            s = random.randint(115, 145)
            d = random.randint(72, 92)
            WatchBloodPressure.objects.create(watch_sync=watchsync, systolic=s, diastolic=d, pulse=random.randint(60,90), recorded_at=ts, raw={})

        self.stdout.write(self.style.SUCCESS('Sample manual and watch readings created for user: %s' % username))
