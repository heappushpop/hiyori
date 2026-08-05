from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Client
from xray.api import Xray


@receiver(post_delete, sender=Client)
def post_delete_handler(sender, instance, **kwargs):
    Xray().remove_user(instance.name)


@receiver(pre_save, sender=Client)
def pre_save_handler(sender, instance, **kwargs):
    try:
        client = Client.objects.get(id=instance.id)
    except Client.DoesNotExist:
        return

    Xray().remove_user(client.name)
