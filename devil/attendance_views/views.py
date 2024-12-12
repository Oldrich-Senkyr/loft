from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from reader.models import AttendanceEvent, Person
from agent.models import Person

def create_attendance_event(request):
    if request.method == "POST":
        person_id = request.POST.get("person")
        event_type = request.POST.get("event_type")
        event_time = request.POST.get("event_time")
        departure_reason = request.POST.get("departure_reason", "illegal")

        # Kontrola vyplnění všech polí
        if not all([person_id, event_type, event_time]):
            error_message = _("All fields are required.")
            return render(request, "devil/attendance_event_form.html", {
                "error_message": error_message,
                "persons": Person.objects.all(),
                "event_types": AttendanceEvent.EVENT_TYPES,
                "departure_reasons": AttendanceEvent.DEPARTURE_REASONS,
            })

        # Speciální kontrola pro typ události work_start nebo work_end
        if event_type in ["work_start", "work_end"]:
            departure_reason = ""
                
        # Vytvoření nového záznamu
        AttendanceEvent.objects.create(
            person_id=person_id,
            event_type=event_type,
            event_time=event_time,
            departure_reason=departure_reason,
        )
        return redirect("devil/attendance_event_list")  # Přesměrování na seznam událostí

    return render(request, "devil/attendance_event_form.html", {
        "persons": Person.objects.all(),
        "event_types": AttendanceEvent.EVENT_TYPES,
        "departure_reasons": AttendanceEvent.DEPARTURE_REASONS,
    })
