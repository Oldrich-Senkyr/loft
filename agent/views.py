from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from .models import Person
from datetime import datetime
from django.conf import settings


# Create your views here.
# vylistuj persons ........................................................................................................
def persons_list(request):
    persons = Person.objects.all()
    context = {
        'template_name': 'agent/list.html',  # Přidání názvu šablony
        'persons': persons,
        'title': _("Persons List"),  # Přidání překladu pro titulek
    }
    return render(request, 'agent/list.html', context)


def person_detail(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    current_year = datetime.now().year
    current_month = datetime.now().month
    context = {
        'person': person,
        'year': current_year,
        'month': current_month,
        'template_name': 'agent/person_detail.html',  # Přidání názvu šablony
    }
    return render(request, 'agent/person_detail.html', context)


