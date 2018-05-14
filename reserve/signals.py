from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import RepeatReserveTime
from .utils import do_repeat_single


@receiver(post_save, sender=RepeatReserveTime, dispatch_uid='RepeatReserveTime_post_save')
def repeat_reserve_time_save(sender, instance, created, raw, using, update_fields, **kwargs):
    if created:
        do_repeat_single(rrt_id=instance.id)
