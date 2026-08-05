from asgiref.sync import sync_to_async
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_safe


@require_safe
async def index(request):
    return await sync_to_async(render)(request, "index.html")


@require_POST
async def lockout(request, credentials, *args, **kwargs):
    return await sync_to_async(render)(request, "lockout.html", status=429)
