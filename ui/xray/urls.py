from django.urls import path

from .views import online, stats

app_name = 'xray'

urlpatterns = [
    path('online/', online, name='online'),
    path('stats/', stats, name='stats'),
]
