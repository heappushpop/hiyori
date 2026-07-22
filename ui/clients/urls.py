from django.urls import path

from .views import add, client, index, remove

app_name = 'clients'

urlpatterns = [
    path('', index, name='index'),
    path('<int:id>/', client, name='client'),
    path('add/', add, name='add'),
    path('remove/', remove, name='remove'),
]
