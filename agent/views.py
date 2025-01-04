from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from .models import Person, Company, Division, Team, PersonCompany
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


from django.shortcuts import render
from django.utils.translation import gettext as _
from .models import Person, Company, PersonCompany

def persons_list_with_companies(request):
    # Fetch all persons
    persons = Person.objects.all()

    # Create a list of persons with their associated companies
    persons_with_companies = []
    for person in persons:
        # Get all companies where the person is employed through PersonCompany
        companies = Company.objects.filter(company_persons__person=person)  # Use the correct related_name
        persons_with_companies.append({
            'person': person,
            'companies': companies
        })

    # Add context for rendering the template
    context = {
        'template_name': 'agent/list_with_companies.html',  # Corrected template name
        'persons_with_companies': persons_with_companies,  # Persons and their companies
        'title': _("Persons List"),  # Title with translation support
    }

    return render(request, 'agent/list_with_companies.html', context)





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


from django.shortcuts import get_object_or_404, redirect, render
from django import forms  # Import forms here
from django.forms import ModelForm, ModelMultipleChoiceField
from .models import Person, Company, PersonCompany
from django.utils.translation import gettext_lazy as _

# Form for editing a person and assigning companies
class PersonEditForm(ModelForm):
    companies = ModelMultipleChoiceField(
        queryset=Company.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label=_("Companies"),
    )

    class Meta:
        model = Person
        fields = ['first_name', 'last_name', 'display_name', 'role', 'companies']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate the companies field with the current assignments
        if self.instance.pk:
            self.fields['companies'].initial = Company.objects.filter(
                company_persons__person=self.instance
            )

def edit_person(request, pk):
    person = get_object_or_404(Person, pk=pk)

    if request.method == "POST":
        form = PersonEditForm(request.POST, instance=person)
        if form.is_valid():
            # Save the person
            person = form.save()

            # Update Person-Company relationships
            selected_companies = form.cleaned_data['companies']
            PersonCompany.objects.filter(person=person).exclude(company__in=selected_companies).delete()
            for company in selected_companies:
                PersonCompany.objects.get_or_create(person=person, company=company)

            return redirect('agent:persons_list_with_companies')  # Replace with your person list view name

    else:
        form = PersonEditForm(instance=person)

    context = {
        'form': form,
        'person': person,
        'title': _("Edit Person"),
    }
    return render(request, 'agent/edit_person.html', context)


