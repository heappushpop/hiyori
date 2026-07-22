from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from clients.models import Client
from stats.models import Stat
from xray.api import Xray


@login_required
@require_GET
async def online(request):
    return JsonResponse({'names': Xray().online()})


@api_view(['POST'])
def stats(request):
    stats = Xray().stats()

    for name in stats:
        if stats[name]['uplink'] == 0 and stats[name]['downlink'] == 0:
            continue

        stat = Stat(
            client=Client.objects.get(name=name),
            created_at=stats[name]['created_at'],
            downlink=stats[name]['downlink'],
            uplink=stats[name]['uplink'],
        )
        stat.full_clean()
        stat.save()

    return Response(status=HTTP_201_CREATED)
