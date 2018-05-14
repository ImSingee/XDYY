from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, UserInfo


@receiver(post_save, sender=User, dispatch_uid='post_save')
def user_save(sender, instance, created, raw, using, update_fields, **kwargs):
    if created:
        ui = UserInfo(user=instance)
        ui.save()
