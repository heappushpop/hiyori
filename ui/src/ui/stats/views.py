from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_safe

from clients.models import Client


@login_required
@require_safe
async def index(request):
    clients = [client async for client in Client.objects.order_by("-created_at")]

    return await sync_to_async(render)(
        request, "stats/index.html", {"clients": clients}
    )
