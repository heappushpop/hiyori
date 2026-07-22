from asgiref.sync import sync_to_async
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
async def index(request):
    return await sync_to_async(render)(request, 'home/index.html')
