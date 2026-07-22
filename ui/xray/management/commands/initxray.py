from django.core.management.base import BaseCommand

from clients.models import Client
from xray.api import Xray


class Command(BaseCommand):
    help = 'Initialize xray'

    def handle(self, *args, **options):
        Xray().init()

        for client in Client.objects.all():
            client.save()
