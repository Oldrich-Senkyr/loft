
# Create your views here.

from .models import AttendanceEvent, Person  # Ensure you import the Person model
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework.exceptions import NotFound
from django.shortcuts import render, get_object_or_404, redirect
from .forms import AttendanceEventForm
from django.http import Http404
from datetime import datetime
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils.http import urlencode

from django.http import Http404

from datetime import datetime, time
from django.contrib import messages


from django.contrib import messages

@csrf_exempt
@api_view(['POST'])
def receive_event(request):
    # Check if a POST request was received
    if request.method == 'POST':
        # Retrieve data from the request body (JSON)
        event_type = request.data.get('event_type')
        event_time = request.data.get('event_time')
        arrival_reason = request.data.get('arrival_reason')
        departure_reason = request.data.get('departure_reason')
        person_id = request.data.get('person')  # Expecting person_id here
        timestamp = request.data.get('timestamp', timezone.now())

        # Validate event_type
        if event_type not in dict(AttendanceEvent.EVENT_TYPES):
            return Response({"error": "Invalid event type."}, status=status.HTTP_400_BAD_REQUEST)

        # Set reasons based on event_type
        if event_type == 'work_start' and arrival_reason not in dict(AttendanceEvent.ARRIVAL_REASONS):
            return Response({"error": "Invalid arrival reason."}, status=status.HTTP_400_BAD_REQUEST)
        if event_type == 'work_end' and departure_reason not in dict(AttendanceEvent.DEPARTURE_REASONS):
            return Response({"error": "Invalid departure reason."}, status=status.HTTP_400_BAD_REQUEST)

        # Attempt to retrieve the Person instance based on person_id
        try:
            person = Person.objects.get(id=person_id)  # Retrieve the person instance
        except Person.DoesNotExist:
            return Response({"error": "Person not found."}, status=status.HTTP_404_NOT_FOUND)

        # Attempt to create the attendance event
        try:
            event = AttendanceEvent.objects.create(
                person=person,  # Assign the actual Person instance
                event_type=event_type,
                event_time=event_time,
                timestamp=timestamp,
                arrival_reason=arrival_reason if event_type == 'work_start' else None,
                departure_reason=departure_reason if event_type == 'work_end' else None
            )
            return Response({"message": "Event received", "event_id": event.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"error": "Invalid method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def event_detail(request, event_id):
    event = get_object_or_404(AttendanceEvent, id=event_id)
    current_year = datetime.now().year
    current_month = datetime.now().month
    context = {
        'event': event,
    }
    return render(request, 'reader/event_detail.html', context)

# Create your views here.
# vylistuj eventss ........................................................................................................


def events_list(request):


    event_types = {
        1: _("Start of working hours"),
        2: _("End of working hours"),
        3: _("Break start"),
        4: _("Break end"),
        5: _("Visit start"),
        6: _("Visit end"),
    }
    
    
    departure_reasons = {
        1: _("Legal"),
        2: _("Illegal"),
    }

    # Filtrovat osoby, které mají přiřazené události
    persons = Person.objects.filter(attendance_events__isnull=False).distinct()
    
    # Získání filtrů z GET požadavku
    person_unique_id = request.GET.get('person')
    event_type = request.GET.get('event_type')
    event_date = request.GET.get('event_date')  # Retrieve event_date from GET request

    # Filtrujte data podle parametrů
    events = AttendanceEvent.objects.all()
    if person_unique_id:
        events = events.filter(person__unique_id=person_unique_id)
    if event_type:
        events = events.filter(event_type=event_type)

    if event_date:
        # Parse event_date to make sure it's a valid date, then filter
        parsed_date = parse_date(event_date)
        if parsed_date:
            events = events.filter(event_time__date=parsed_date)    

    # Sort events by event_time
    events = events.order_by('event_time')  # Use '-' for descending order (from latest to earliest)
    return render(request, 'reader/events_list.html', {
        'events': events,
        'persons': persons,
        'title': "Events List",
        'event_types': event_types,
        'departure_reasons': departure_reasons,        
    })


from django.http import QueryDict

from .models import AttendanceEvent

from django.shortcuts import get_object_or_404, redirect, render
from .forms import AttendanceEventForm
from .models import AttendanceEvent

def edit_attendance_event(request, event_id):
    # Získání instance AttendanceEvent
    event = get_object_or_404(AttendanceEvent, id=event_id)

    # Načtení URL k přesměrování
    redirect_url = request.GET.get('next', None)  # Získání URL z parametru 'next'

    if request.method == 'POST':
        # Vytvoření kopie POST dat
        post_data = request.POST.copy()
        print("POST data:", post_data)

        # Výchozí hodnota departure_reason, pokud chybí
        if 'departure_reason' not in post_data or post_data['departure_reason'] == '':
            post_data['departure_reason'] = str(AttendanceEvent.DepartureReason.NONE)  # Symbolické jméno pro 'N/a'

        # Pokud je typ události začátek/konec přestávky a departure_reason je nedefinováno, nastav 'Illegal'
        if int(post_data['event_type']) in [
            AttendanceEvent.EventType.BREAK_START,
            AttendanceEvent.EventType.BREAK_END,
        ] and post_data['departure_reason'] == str(AttendanceEvent.DepartureReason.NONE):
            post_data['departure_reason'] = str(AttendanceEvent.DepartureReason.ILLEGAL)  # Symbolické jméno pro 'Illegal'

        print("POST data:", post_data)  # Pro ladění

        # Vytvoření formuláře s upravenými daty
        form = AttendanceEventForm(post_data, instance=event)

        if form.is_valid():
            print("Form cleaned data:", form.cleaned_data)  # Ladění: zobrazení vyčištěných dat
            form.save()
            # Přesměrování na zadanou URL nebo výchozí seznam událostí
            return redirect(redirect_url or 'reader_i18n:events_list')
        else:
            print("Form errors:", form.errors)  # Ladění: zobrazení chyb formuláře
        
        # Přesměrování zpět na původní URL
        if redirect_url:
            return redirect(redirect_url)
        return redirect("reader_i18n:events_list")  # Fallback, pokud není žádná URL v request    
    
    else:
        # Předvyplnění formuláře daty instance
        form = AttendanceEventForm(instance=event)
        form.fields['event_type'].initial = event.event_type
        form.fields['event_time'].initial = event.event_time
        form.fields['departure_reason'].initial = event.departure_reason

    return render(request, 'reader/edit_attendance_event.html', {
        'form': form,
        'event': event,
        'redirect_url': redirect_url,  # Předání redirect_url do šablony
    })

 




def select_person_and_date(request):
    if request.method == 'POST':
        person_id = request.POST.get('person')
        event_date = request.POST.get('event_date')

        # Uložení vybrané osoby a data do session
        request.session['person_id'] = person_id
        request.session['event_date'] = event_date

        # Přesměrování na přidání události
        return redirect('reader_i18n:add_attendance_event')

    # Získání seznamu osob pro výběr
    persons = Person.objects.all()
    return render(request, 'reader/select_person_and_date.html', {'persons': persons})




from django.shortcuts import render, redirect, get_object_or_404
from .forms import AttendanceEventForm
from .models import Person, AttendanceEvent




def add_attendance_event(request):
    # Handle POST requests (form submission)
    if request.method == 'POST':
        print(f"POST data: {request.POST}")  # Výstup POST dat pro kontrolu
        person_id = request.POST.get('person')
        event_date_time_str = request.POST.get('event_time')  # Retrieve event_date_time from POST
        print(f"person_id: {person_id}")
        print(f"event_date_time_str: {event_date_time_str}")

        # Save person_id and event_date_time_str to session if available
        if person_id:
            request.session['person_id'] = person_id
        if event_date_time_str:
            request.session['event_date_time'] = event_date_time_str

        form = AttendanceEventForm(request.POST)
        if form.is_valid():
            person = get_object_or_404(Person, id=person_id)

            # Parse event_date_time_str
            if event_date_time_str:
                try:
                    event_date_time = timezone.datetime.strptime(event_date_time_str, '%Y-%m-%dT%H:%M')
                except (ValueError, TypeError):
                    event_date_time = None  # Handle invalid or missing event date/time
            else:
                event_date_time = None

            if event_date_time:
                event = form.save(commit=False)
                event.person = person
                event.event_time = timezone.make_aware(event_date_time)
                event.timestamp = timezone.now()
                event.save()
                return redirect('reader_i18n:events_list')
            else:
                form.add_error(None, 'Event date and time are required.')
        else:
            print(f"Form errors: {form.errors}")  # Tiskne chyby formuláře, pokud nějaké existují
    else:  # Handle GET requests (initialize form with session data)
        person_id = request.session.get('person_id')
        event_date_time_str = request.session.get('event_date_time')

        # If no event date/time is in the session, use the current date and time
        if not event_date_time_str:
            event_date_time_str = timezone.now().strftime('%Y-%m-%dT%H:%M')  # Set current datetime as default

        # Redirect if session data is missing
        if not person_id:
            return redirect('reader_i18n:select_person_and_date')

        form = AttendanceEventForm(initial={'event_date_time': event_date_time_str})

    # Retrieve the person for rendering
    person = get_object_or_404(Person, id=person_id)

    # Render the form in the template with the required context
    return render(
        request,
        'reader/add_attendance_event.html',
        {'form': form, 'person': person, 'event_date_time': event_date_time_str}
    )



def delete_event(request, event_id):
    # Získáme událost podle ID nebo vrátíme 404, pokud neexistuje
    event = get_object_or_404(AttendanceEvent, id=event_id)

    if request.method == "POST":
        # Načtení URL k přesměrování z POST dat
        redirect_url = request.POST.get('redirect_url', None)  # Získání URL z hidden inputu

        # Smazání události
        event.delete()

        # Zobrazení zprávy o úspěchu
        messages.success(request, 'Záznam byl úspěšně smazán.')

        # Přesměrování zpět na původní URL
        if redirect_url:
            return redirect(redirect_url)
        return redirect('reader_i18n:events_list')  # Výchozí přesměrování

    # Pokud není metoda POST, přesměrujeme uživatele na seznam
    return redirect('reader_i18n:events_list')


def snk_delete_add_attendance_event_from_list_view (request):
    # Handle POST requests (form submission)
    if request.method == 'POST':
        print(f"POST data: {request.POST}")  # Výstup POST dat pro kontrolu
        person_id = request.POST.get('person')
        event_date_time_str = request.POST.get('event_time')  # Retrieve event_date_time from POST
        print(f"person_id: {person_id}")
        print(f"event_date_time_str: {event_date_time_str}")

        # Save person_id and event_date_time_str to session if available
        if person_id:
            request.session['person_id'] = person_id
        if event_date_time_str:
            request.session['event_date_time'] = event_date_time_str

        form = AttendanceEventForm(request.POST)
        if form.is_valid():
            person = get_object_or_404(Person, id=person_id)

            # Parse event_date_time_str
            if event_date_time_str:
                try:
                    event_date_time = timezone.datetime.strptime(event_date_time_str, '%Y-%m-%dT%H:%M')
                except (ValueError, TypeError):
                    event_date_time = None  # Handle invalid or missing event date/time
            else:
                event_date_time = None

            if event_date_time:
                event = form.save(commit=False)
                event.person = person
                event.event_time = timezone.make_aware(event_date_time)
                event.timestamp = timezone.now()
                event.save()
                return redirect('reader_i18n:events_list')
            else:
                form.add_error(None, 'Event date and time are required.')
        else:
            print(f"Form errors: {form.errors}")  # Tiskne chyby formuláře, pokud nějaké existují
    else:  # Handle GET requests (initialize form with session data)
        person_id = request.session.get('person_id')
        event_date_time_str = request.session.get('event_date_time')

        # If no event date/time is in the session, use the current date and time
        if not event_date_time_str:
            event_date_time_str = timezone.now().strftime('%Y-%m-%dT%H:%M')  # Set current datetime as default

        # Redirect if session data is missing
        if not person_id:
            return redirect('reader_i18n:select_person_and_date')

        form = AttendanceEventForm(initial={'event_date_time': event_date_time_str})

    # Retrieve the person for rendering
    person = get_object_or_404(Person, id=person_id)

    # Render the form in the template with the required context
    return render(
        request,
        'reader/add_attendance_event.html',
        {'form': form, 'person': person, 'event_date_time': event_date_time_str}
    )


from django.http import QueryDict


def create_attendance_event(request):
    if request.method == "POST":
        person_id = request.POST.get("person")
        event_type = request.POST.get("event_type")
        event_time = request.POST.get("event_time")
        departure_reason = request.POST.get("departure_reason", "illegal")
        redirect_url = request.POST.get("redirect_url", None)  # Načtení URL k přesměrování

        # Kontrola vyplnění všech polí
        if not all([person_id, event_type, event_time]):
            messages.error(request, _("All fields are required."))
            if redirect_url:  # Vrátíme se na předchozí filtrovanou URL
                return redirect(redirect_url)
            return redirect("reader:events_list")

       # Kontrola na existenci duplicitního záznamu
        try:
            # Parse the event_time into a datetime object and ensure it's timezone-aware
            event_time = timezone.make_aware(datetime.fromisoformat(event_time))
        except ValueError:
            messages.error(request, _("Invalid date/time format."))
            if redirect_url:
                return redirect(redirect_url)
            return redirect("reader:events_list")

        # Check for duplicates only for WORK_START and WORK_END event types
        if event_type in [
            str(AttendanceEvent.EventType.WORK_START),
            str(AttendanceEvent.EventType.WORK_END),
        ]:
            existing_event = AttendanceEvent.objects.filter(
                person_id=person_id,
                event_type=event_type,
                event_time__date=event_time.date()  # Compare only the date part
            ).exists()

            if existing_event:
                if event_type in [ str(AttendanceEvent.EventType.WORK_START),]:
                    messages.error(request, _("An entry for the start of working time already exists!"))
                if event_type in [ str(AttendanceEvent.EventType.WORK_END),]:
                    messages.error(request, _("An entry for the end of working time already exists!"))
                if redirect_url:  # Redirect back to the original filtered URL
                    return redirect(redirect_url)
                return redirect("reader:events_list")
       
        # Vytvoření nového záznamu
        AttendanceEvent.objects.create(
            person_id=person_id,
            event_type=event_type,
            event_time=event_time,
            departure_reason=departure_reason,
        )

        # Přesměrování zpět na původní URL
        if redirect_url:
            return redirect(redirect_url)
        return redirect("reader:events_list")  # Fallback, pokud není žádná URL v requestu

    # Načtení dotazových parametrů pro filtrovaný seznam
    query_params = urlencode(request.GET)
    redirect_url = f"{request.path}?{query_params}"

    return render(request, "reader/events_list.html", {
        "persons": Person.objects.all(),
        "event_types": AttendanceEvent.EVENT_TYPES,
        "departure_reasons": AttendanceEvent.DEPARTURE_REASONS,
        "redirect_url": redirect_url,  # Předání URL pro návrat
    })
