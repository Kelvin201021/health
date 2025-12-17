from django.utils.deprecation import MiddlewareMixin
from hypertension.models import Device


class DeviceTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Token "):
            request.device = None
            return

        token_value = auth_header.replace("Token ", "").strip()

        try:
            request.device = Device.objects.get(token=str(token_value))
        except Device.DoesNotExist:
            request.device = None