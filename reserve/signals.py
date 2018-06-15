from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm

from .models import RepeatReserveTime, ReserveRecord, ReserveTime
from .utils import do_repeat_single


@receiver(post_save, sender=RepeatReserveTime, dispatch_uid='RepeatReserveTime_post_save')
def repeat_reserve_time_post_save(sender, instance, created, raw, using, update_fields, **kwargs):
    if instance.reservee:
        assign_perm('reserve.change_repeatreservetime', instance.reservee, instance)
        assign_perm('reserve.disable_repeatreservetime', instance.reservee, instance)
    if created:
        do_repeat_single(rrt_id=instance.id)


# @receiver(pre_save, sender=ReserveRecord, dispatch_uid='ReserveRecord_pre_save')
# def reserve_record_pre_save(sender, instance, **kwargs):
#     if instance.reserver:
#         remove_perm('reserve.confirm', instance.reserver, instance)


@receiver(post_save, sender=ReserveRecord, dispatch_uid='ReserveRecord_post_save')
def reserve_record_post_save(sender, instance, created, raw, using, update_fields, **kwargs):
    if instance.main_time.reservee:
        assign_perm('reserve.confirm', instance.main_time.reservee, instance)
        assign_perm('reserve.reject_reserverecord', instance.main_time.reservee, instance)
        assign_perm('reserve.absent_reserverecord', instance.main_time.reservee, instance)
        assign_perm('reserve.cancel_reserverecord', instance.main_time.reservee, instance)


# @receiver(pre_save, sender=ReserveTime, dispatch_uid='ReserveTime_pre_save')
# def reserve_time_pre_save(sender, instance, **kwargs):
#     if instance.reservee:
#         remove_perm('reserve.disable', instance.reservee, instance)


@receiver(post_save, sender=ReserveTime, dispatch_uid='ReserveTime_post_save')
def reserve_time_post_save(sender, instance, created, raw, using, update_fields, **kwargs):
    if instance.reservee:
        assign_perm('reserve.disable', instance.reservee, instance)
        assign_perm('reserve.edit_max', instance.reservee, instance)
