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
from .models import Employee

@permission_required('app_name.view_team_data')
def team_members(request):
    team = request.user.employee.team
    members = Employee.objects.filter(team=team)
    return render(request, 'team_members.html', {'members': members})

@permission_required('app_name.edit_team_data')
def edit_team_member(request, member_id):
    member = get_object_or_404(Employee, pk=member_id)
    if member.team == request.user.employee.team:
        if request.method == "POST":
            # vaše logika pro editaci
            pass
        return render(request, 'edit_team_member.html', {'member': member})
    else:
        return redirect('not_allowed')  # Případ, kdy uživatel nemá oprávnění editovat


from django.shortcuts import render

def team_list(request):
    user = request.user
    teams = get_accessible_teams(user)
    return render(request, 'team_list.html', {'teams': teams})

from django.shortcuts import get_object_or_404

def team_detail(request, team_id):
    team = get_object_or_404(get_accessible_teams(request.user), id=team_id)
    members = get_accessible_team_members(request.user).filter(team=team)
    return render(request, 'team_detail.html', {'team': team, 'members': members})


def division_list(request):
    divisions = get_accessible_divisions(request.user)
    return render(request, 'division_list.html', {'divisions': divisions})



def get_accessible_companies(user):
    if user.employee.role == 'manager':
        return Company.objects.all()
    return Company.objects.none()

def get_accessible_divisions(user):
    if user.employee.role == 'manager':
        return Division.objects.all()
    elif user.employee.role == 'division_leader':
        return Division.objects.filter(id=user.employee.division_id)
    return Division.objects.none()

def get_accessible_teams(user):
    if user.employee.role == 'manager':
        return Team.objects.all()
    elif user.employee.role == 'division_leader':
        return Team.objects.filter(division=user.employee.division)
    elif user.employee.role == 'team_leader':
        return Team.objects.filter(id=user.employee.team_id)
    return Team.objects.none()

def get_accessible_team_members(user):
    if user.employee.role == 'manager':
        return Employee.objects.all()
    elif user.employee.role == 'division_leader':
        teams = Team.objects.filter(division=user.employee.division)
        return Employee.objects.filter(team__in=teams)
    elif user.employee.role == 'team_leader':
        return Employee.objects.filter(team=user.employee.team)
    return Employee.objects.none()

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