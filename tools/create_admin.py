import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core_fixed.settings')
import django
django.setup()
from django.contrib.auth.models import User

u = 'devadmin'
p = 'DevAdminPass123!'
if User.objects.filter(username=u).exists():
    print('EXISTS')
else:
    User.objects.create_superuser(u, 'devadmin@example.com', p)
    print('CREATED')
