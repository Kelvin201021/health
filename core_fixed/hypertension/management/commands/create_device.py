from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.apps import apps


class Command(BaseCommand):
    help = 'Create a Device token for a user. Usage: manage.py create_device <username> [--name NAME]'

    def add_arguments(self, parser):
        parser.add_argument('username', help='Username to create device for')
        parser.add_argument('--name', '-n', default='Spoon', help='Device friendly name')

    def handle(self, *args, **options):
        username = options['username']
        name = options.get('name')
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User '{username}' does not exist")

        Device = apps.get_model('hypertension', 'Device')
        device = Device.objects.create(user=user, name=name)
        self.stdout.write(self.style.SUCCESS('Created device:'))
        self.stdout.write(f'  id: {device.id}')
        self.stdout.write(f'  name: {device.name}')
        self.stdout.write(f'  token: {device.token}')
        self.stdout.write('Store this token securely and configure the spoon to use it when posting readings.')
