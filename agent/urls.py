from django.urls import path
from .views import persons_list, person_detail, company_hierarchy, persons_list_with_companies, edit_person

app_name = 'agent'

urlpatterns = [
    path('list/', persons_list, name='persons_list'),
    path('list-with-companies/', persons_list_with_companies, name='persons_list_with_companies'),
    path('person/<int:person_id>/', person_detail, name='person_detail'),  # Přidejte tuto řádku
    path('company-hierarchy/', company_hierarchy, name='company_hierarchy'),
    path('person/<int:pk>/edit/', edit_person, name='edit_person'),
]
