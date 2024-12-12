from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse
from eval.models import WorkDay, WorkDayAssignment
from order.forms import WorkDayAssignmentForm
from django.utils.translation import gettext_lazy as _

def workday_assignments(request, employee_id, date):
    # Načtení pracovního dne daného zaměstnance
    workday = get_object_or_404(WorkDay, employee_id=employee_id, date=date)

    # Seznam stávajících přiřazení
    assignments = workday.assignments.all()
    total_assigned_hours = sum(a.assigned_hours for a in assignments)

    # Spočítáme nevyužité hodiny, ale ignorujeme intervaly menší než 0.5 hodiny
    unassigned_hours = workday.total_work_hours - total_assigned_hours
    if unassigned_hours < 0.5:
        unassigned_hours = 0  # Ignorujeme příliš malé intervaly

    # Zpracování formuláře pro nové přiřazení
    if request.method == "POST":
        form = WorkDayAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.workday = workday

            # Kontrola, zda nepřekračuje nevyužité hodiny a splňuje minimální limit
            if assignment.assigned_hours > unassigned_hours:
                messages.error(
                    request,
                    _("Cannot assign more hours than available. Remaining: %(hours)s")
                    % {'hours': unassigned_hours}
                )
            elif assignment.assigned_hours < 0.5:
                messages.error(
                    request,
                    _("Assigned hours must be at least 0.5 hours.")
                )
            else:
                # Pokusíme se najít existující přiřazení nebo vytvořit nové
                obj, created = WorkDayAssignment.objects.update_or_create(
                    workday=workday,
                    project=assignment.project,
                    defaults={'assigned_hours': assignment.assigned_hours, 'work_performed': assignment.work_performed}
                )
                
                if created:
                    messages.success(request, _("Assignment added successfully."))
                else:
                    messages.success(request, _("Assignment updated successfully."))

                return redirect(reverse('order:workday_assignments', args=[employee_id, date]))
    else:
        form = WorkDayAssignmentForm()

    return render(request, 'order/workday_assignments.html', {
        'workday': workday,
        'assignments': assignments,
        'unassigned_hours': unassigned_hours,
        'form': form,
    })
