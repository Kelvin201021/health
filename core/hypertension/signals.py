from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """
    Safe signal: try to fetch the Profile model at runtime.
    If the model is not yet available (LookupError), skip gracefully.
    """
    try:
        Profile = apps.get_model('hypertension', 'Profile')
    except LookupError:
        # The Profile model isn't ready yet (Django startup). Skip silently.
        logger.warning("Profile model not ready; skipping profile creation for user %s", getattr(instance, 'username', None))
        return

    try:
        if created:
            Profile.objects.create(user=instance)
        else:
            Profile.objects.get_or_create(user=instance)
    except Exception as e:
        # Catch unexpected DB errors so signal doesn't crash management commands.
        logger.exception("Failed creating/updating Profile for user %s: %s", getattr(instance, 'username', None), str(e))
