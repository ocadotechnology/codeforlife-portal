from django.core.cache import cache
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django_otp.models import Device

from common.utils import two_factor_cache_key


@receiver([post_save, pre_delete])
def clear_two_factor_cache(sender, **kwargs):
    if issubclass(sender, Device):
        user = kwargs["instance"].user
        cache.delete(two_factor_cache_key(user))
