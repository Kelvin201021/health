#!/usr/bin/env python3
import os
import sys
import django
import json
import urllib.request
import urllib.error
from django.utils import timezone

# Configure Django settings module path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_fixed.settings')
# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

django.setup()

from django.contrib.auth import get_user_model
from django.apps import apps

User = get_user_model()
username = 'testdevice'
email = 'testdevice@example.com'
password = 'TestPass123!'

user, created = User.objects.get_or_create(username=username, defaults={'email': email})
if created:
    user.set_password(password)
    user.save()
    print('Created user', username)
else:
    print('User exists', username)

Device = apps.get_model('hypertension', 'Device')
# create device
device = Device.objects.create(user=user, name='SpoonTest')
print('Created device token:', device.token)

# POST a test reading
url = 'http://127.0.0.1:8000/dashboard/api/sodium/add-meal/'
headers = {'Authorization': f'Token {device.token}', 'Content-Type': 'application/json'}
payload = {
    'name': 'Test spoon',
    'sodium_mg': 150,
    'portion': 'spoon',
    'recorded_at': timezone.now().strftime('%Y-%m-%dT%H:%M:%S')
}
data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers=headers, method='POST')
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode('utf-8')
        print('POST status:', resp.getcode())
        print('Response:', body)
except urllib.error.HTTPError as e:
    try:
        print('POST status:', e.code)
        print('Response:', e.read().decode('utf-8'))
    except Exception:
        print('HTTPError', e)
except Exception as e:
    print('POST failed:', e)
