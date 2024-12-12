from django.urls import path
from .views import persons_list, person_detail

app_name = 'agent'

urlpatterns = [
    path('list/', persons_list, name='persons_list'),
    path('person/<int:person_id>/', person_detail, name='person_detail'),  # Přidejte tuto řádku
]
