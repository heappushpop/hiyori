from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required
from django.contrib.messages import error, success
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import aget_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .models import Client


@login_required
@require_POST
async def add(request):
    name = request.POST.get('name')

    if not name:
        error(request, 'Name field cannot be empty')

        return redirect('clients:index')

    try:
        client = Client(name=name)
        await sync_to_async(client.full_clean)()
        await client.asave()
    except ValidationError:
        error(request, f'Client with name {name} already exists')

        return redirect('clients:index')

    success(request, 'A new client was successfully added')

    return redirect(client)


@login_required
@require_GET
async def client(request, id):
    client = await aget_object_or_404(Client, id=id)

    return await sync_to_async(render)(
        request, 'clients/client.html', {'client': client}
    )


@login_required
@require_GET
async def index(request):
    clients = [client async for client in Client.objects.order_by('-created_at')]

    return await sync_to_async(render)(
        request, 'clients/index.html', {'clients': clients}
    )


@login_required
@require_POST
async def remove(request):
    id = request.POST.get('id')

    if not id:
        return HttpResponse(status=422)

    try:
        client = await Client.objects.aget(id=id)
        await client.adelete()
    except Client.DoesNotExist:
        return HttpResponse(status=422)

    success(request, 'A client was successfully removed')

    return redirect('clients:index')
