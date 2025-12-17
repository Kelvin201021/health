import logging
from django.utils.deprecation import MiddlewareMixin

from .models import Device

logger = logging.getLogger(__name__)


class DeviceTokenMiddleware(MiddlewareMixin):
    """Middleware that maps a device token (Authorization: Token <token> or X-Device-Token)
    to `request.device` and sets `request.user` to the device owner for the request.
    """

    def process_request(self, request):
        token = None
        auth_hdr = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_hdr:
            if auth_hdr.lower().startswith('token '):
                token = auth_hdr.split(None, 1)[1].strip()
            else:
                token = auth_hdr.strip()
        if not token:
            token = request.META.get('HTTP_X_DEVICE_TOKEN')

        if not token:
            request.device = None
            return None

        try:
            device = Device.objects.get(token=token)
            request.device = device
            # override request.user for this request so views act on behalf of device owner
            request.user = device.user
            logger.debug('Device token accepted for user %s', device.user)
        except Device.DoesNotExist:
            request.device = None
            logger.debug('Invalid device token presented')

        return None
