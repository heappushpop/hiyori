from django.db.models import CASCADE, DateTimeField, ForeignKey, IntegerField, Model

from clients.models import Client


class Stat(Model):
    client = ForeignKey(Client, on_delete=CASCADE)
    created_at = DateTimeField()
    down = IntegerField()
    up = IntegerField()
