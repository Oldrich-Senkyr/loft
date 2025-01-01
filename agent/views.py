from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from .models import Person, Company, Division, Team
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


from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404, redirect



def company_hierarchy(request):
    # Předpoklad: Máte pouze jednu společnost, jinak přidejte filtraci
    company = Company.objects.prefetch_related(
        'divisions__teams__leader',  # Corrected from 'leaders' to 'leader'
        'divisions__leader',  # Add this if you want to prefetch the leader of each division
    ).first()

    context = {
        'company': company,
    }
    return render(request, 'agent/company_hierarchy.html', context)


from django.shortcuts import render
from .models import Company, Division, Team

def company_hierarchy(request):
    """
    Displays the hierarchy of companies, divisions, and teams, including their leaders.
    """
    companies = Company.objects.prefetch_related(
        'divisions__teams',
        'leader',
        'divisions__leader',
        'divisions__teams__leader'
    ).all()

    context = {
        'companies': companies
    }
    return render(request, 'agent/company_hierarchy.html', context)
