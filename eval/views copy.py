from django.shortcuts import render, get_object_or_404, redirect
# Create your views here.
from django.db.models import Q, F, Sum, ExpressionWrapper, DateField
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import datetime, timedelta
from reader.models import AttendanceEvent
from eval.models import WorkDay
from agent.models import Person



def attendance_events_by_person_and_date(request, person_id, date):
    # Získání osoby na základě ID
    person = get_object_or_404(Person, pk=person_id)

    # Převod řetězce na objekt datetime
    try:
        selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return render(request, 'error.html', {'message': 'Nesprávný formát data. Použijte YYYY-MM-DD.'})

    # Filtrování událostí podle osoby a data
    events = AttendanceEvent.objects.filter(person=person, timestamp__date=selected_date)

    return render(request, 'eval/attendance_events.html', {'events': events, 'selected_date': selected_date, 'person': person})


def subtract_time(time1, time2):
    """
    Odečte dvě hodnoty ve formátu (hours, minutes).
    """
    hours1, minutes1 = time1
    hours2, minutes2 = time2
    
    # Převod na celkové minuty
    total_minutes1 = hours1 * 60 + minutes1
    total_minutes2 = hours2 * 60 + minutes2
    
    # Odečtení minut
    result_minutes = total_minutes1 - total_minutes2
    
    # Převedení výsledných minut zpět na hodiny a minuty
    result_hours, result_minutes = divmod(result_minutes, 60)
    
    # Pokud je výsledek záporný, přidáme 24 hodin k hodinám
    if result_minutes < 0:
        result_minutes += 60
        result_hours -= 1

    if result_hours < 0:
        result_hours += 24  # nebo ošetřit jinak podle potřeby (např. vrátit 0)
    
    return result_hours, result_minutes


def monthly_work_hours(request, person_id, year, month):
    # Create timezone-aware start and end dates
    start_date = timezone.make_aware(datetime(year, month, 1))
    end_date = (start_date + timedelta(days=31)).replace(day=1)

    # Get the person object
    person = get_object_or_404(Person, pk=person_id)

    # Filter attendance events for the person and the specified month
    events = AttendanceEvent.objects.filter(
        person=person,
        event_time__gte=start_date,
        event_time__lt=end_date
    ).order_by('event_time')

    # Calculate daily work hours using the updated function
    daily_work_hours, daily_break_hours, work_start_end_times = calculate_daily_work_hours(events, person)

    daily_summary = []
    for date in daily_work_hours.keys():
        daily_summary.append({
            'date': date,
            'work_hours': daily_work_hours[date],  # work_hours are now in (hours, minutes)
            'legal_break_hours': daily_break_hours['legal'].get(date, (0, 0)),  # legal_break_hours in (hours, minutes)
            'illegal_break_hours': daily_break_hours['illegal'].get(date, (0, 0)),  # illegal_break_hours in (hours, minutes)
            'start_time': work_start_end_times.get(date, {}).get('start'),
            'end_time': work_start_end_times.get(date, {}).get('end'),
        })

    # Calculate total hours for the month
    monthly_total_hours = (0, 0)  # Initialize total as (hours, minutes)
    for date, work_time in daily_work_hours.items():
        monthly_total_hours = add_time(monthly_total_hours, work_time)

    monthly_total_legal_break_hours = (0, 0)
    for date, break_time in daily_break_hours['legal'].items():
        monthly_total_legal_break_hours = add_time(monthly_total_legal_break_hours, break_time)

    monthly_total_illegal_break_hours = (0, 0)
    for date, break_time in daily_break_hours['illegal'].items():
        monthly_total_illegal_break_hours = add_time(monthly_total_illegal_break_hours, break_time)

    context = {
        'person': person,
        'year': year,
        'month': month,
        'daily_summary': daily_summary,
        'monthly_total_hours': monthly_total_hours,
        'monthly_total_legal_break_hours': monthly_total_legal_break_hours,
        'monthly_total_illegal_break_hours': monthly_total_illegal_break_hours,
    }
    return render(request, 'eval/monthly_summary.html', context)

# Helper function to add time in (hours, minutes) format
def add_time(time1, time2):
    hours1, minutes1 = time1
    hours2, minutes2 = time2
    total_minutes = (hours1 * 60 + minutes1) + (hours2 * 60 + minutes2)
    return divmod(total_minutes, 60)  # Return as (hours, minutes)


def attendance_summary_view(request, person_id):
    if request.method == "POST":
        # Získání hodnoty měsíce z formuláře
        month = request.POST.get("month")
        if month:
            year, month = month.split("-")
        else:
            # Pokud není hodnota zadána, použijeme aktuální měsíc a rok
            now = timezone.now()
            year = now.strftime("%Y")
            month = now.strftime("%m")

        # Přesměrování na URL s rokem a měsícem
        return redirect("eval:monthly_work_hours", person_id=person_id, year=year, month=month)


from datetime import timedelta
from django.utils import timezone


def calculate_daily_work_hours(events,employee):
    debug_print = True
    if debug_print:
        print("\n\n----------------------------------------------------------------\n")
        print("This is calculate_daily_work_hours start.\n")
    daily_work_hours = {}                                       # Vytvori prazdny slovnik, bude mit format ( 2024-11-04: (11.0, 0.0))
    daily_break_hours = {'legal': {}, 'illegal': {}}            # Vytvori prazdny slovnik, bude mit format ( legal: {datetime.date(2024, 11, 4): (1.0, 0.0)) ...} 
                                                                # ilegal: {datetime.date(2024, 11, 4): (1.0, 0.0)) ...}     )
    work_start_end_times = {}

    ongoing_work_period = None                                  # misto pro ulozeni pracovni doby
    ongoing_break_period = None                                 # misto pro ulozeni prestavky
    break_type = None
    break_start_times = []  # To track break start events

    for event in events:                                        # sem se predavaji events filtrovane na mesic a osobu    
        event_time = event.event_time

        # Ensure event_time is timezone aware
        if timezone.is_naive(event_time):
            event_time = timezone.make_aware(event_time)

        date = event_time.date()

        # Initialize daily tracking if not already set
        if date not in daily_work_hours:                                # jestlize den neni jeste ve slovnku inicializuju na zacatku cyklu
            daily_work_hours[date] = timedelta()
            work_start_end_times[date] = {'start': None, 'end': None}
            daily_break_hours['legal'][date] = timedelta()
            daily_break_hours['illegal'][date] = timedelta()

        # Process events by event_type
        if event.event_type == AttendanceEvent.EventType.WORK_START:
            ongoing_work_period = event_time
            work_start_end_times[date]['start'] = event_time

        elif event.event_type == AttendanceEvent.EventType.WORK_END and ongoing_work_period:
            work_duration = event_time - ongoing_work_period
            work_start_end_times[date]['end'] = event_time

            # Adjust work duration if there was an ongoing break
            if ongoing_break_period:
                total_break_duration = event_time - ongoing_break_period
                # Calculate which type of break it is (legal or illegal)
                break_type = 'legal' if event.departure_reason == AttendanceEvent.DepartureReason.LEGAL else 'illegal'
                daily_break_hours[break_type][date] += total_break_duration
                work_duration -= total_break_duration
                ongoing_break_period = None

            # Add work duration to the daily total
            daily_work_hours[date] += work_duration
            ongoing_work_period = None

        elif event.event_type == AttendanceEvent.EventType.BREAK_START:
            ongoing_break_period = event_time
            break_type = 'legal' if event.departure_reason == AttendanceEvent.DepartureReason.LEGAL else 'illegal'
            break_start_times.append((event_time, break_type))  # Track break start times

        elif event.event_type == AttendanceEvent.EventType.BREAK_END:
            # Find the nearest BREAK_START for this BREAK_END
            closest_break_start_time = None
            closest_break_type = None

            for break_start_time, break_type in reversed(break_start_times):  # Traverse in reverse for the closest
                if break_start_time < event_time:
                    closest_break_start_time = break_start_time
                    closest_break_type = break_type
                    break

            if closest_break_start_time:
                break_duration = event_time - closest_break_start_time
                daily_break_hours[closest_break_type][date] += break_duration
                ongoing_break_period = None  # Clear ongoing break period after processing BREAK_END

        # Ensure break end time is cleared after processing
        if ongoing_break_period is None and break_type is not None:
            break_type = None

    # Ensure daily values are zero if no complete work period exists
    for date in daily_work_hours:
        if work_start_end_times[date]['start'] is None or work_start_end_times[date]['end'] is None:
            daily_work_hours[date] = timedelta()
            daily_break_hours['legal'][date] = timedelta()
            daily_break_hours['illegal'][date] = timedelta()
            work_start_end_times[date] = {'start': None, 'end': None}

    # Convert timedelta to (hours, minutes)
    daily_work_hours_in_hours = convert_timedelta_to_hours(daily_work_hours)
    daily_break_hours_in_hours = {
        'legal': convert_timedelta_to_hours(daily_break_hours['legal']),
        'illegal': convert_timedelta_to_hours(daily_break_hours['illegal']),
    }

    # Subtract illegal breaks from work hours
    for date in daily_work_hours_in_hours:
        if date in daily_break_hours_in_hours['illegal']:
            daily_work_hours_in_hours[date] = subtract_time(
                daily_work_hours_in_hours[date], daily_break_hours_in_hours['illegal'][date]
            )

    # Výpis do konzole před návratem
    if debug_print:
        print("\nDelka Daily work hours:", len(daily_work_hours_in_hours),"\n")
        # Iterace přes klíče a hodnoty
        for key, value in daily_work_hours_in_hours.items():
            print(f"{key}: {value}")

        print("\nDaily_break_hours_in_hours:", len(daily_work_hours_in_hours),"\n")
        # Iterace přes klíče a hodnoty
        for key, value in daily_break_hours_in_hours.items():
            print(f"{key}: {value}\n")

        # Iterace přes klíče a hodnoty
        print("\nWork_start_end_times:", len(daily_work_hours_in_hours),"\n")
        for key, value in work_start_end_times.items():
            print(f"{key}: {value}")
        print("\nThis is calculate_daily_work_hours end.")
        print("...........................................................................\n")
    save_work_hours_to_db(employee, daily_work_hours_in_hours, daily_break_hours_in_hours)
    return daily_work_hours_in_hours, daily_break_hours_in_hours, work_start_end_times


# Helper to convert timedelta dictionary to hours and minutes
def convert_timedelta_to_hours(timedelta_dict):
    result = {}
    for date, total_time in timedelta_dict.items():
        total_minutes = total_time.total_seconds() // 60
        hours = total_minutes // 60
        minutes = total_minutes % 60
        result[date] = (hours, minutes)
    return result


# Helper function to subtract time (hours, minutes format)
def subtract_time(time1, time2):
    hours1, minutes1 = time1
    hours2, minutes2 = time2
    total_minutes1 = hours1 * 60 + minutes1
    total_minutes2 = hours2 * 60 + minutes2
    total_minutes = max(0, total_minutes1 - total_minutes2)  # Avoid negative time
    return divmod(total_minutes, 60)  # Return as (hours, minutes)


from django.db import transaction, IntegrityError




from decimal import Decimal

from decimal import Decimal
from django.db import IntegrityError, transaction


from decimal import Decimal
from django.db import IntegrityError
from django.utils.timezone import make_aware
from datetime import datetime

@transaction.atomic
def save_work_hours_to_db(employee, date, work_hours, legal_break_hours, illegal_break_hours, work_start_end_times):
    try:
        # Ujistíme se, že potřebné hodnoty jsou validní
        start_time = work_start_end_times.get('start')
        end_time = work_start_end_times.get('end')

        # Uložíme nebo aktualizujeme záznam v databázi
        workday, created = WorkDay.objects.update_or_create(
            employee=employee,
            date=date,
            defaults={
                'total_work_hours': work_hours,
                'total_legal_break': legal_break_hours,
                'total_illegal_break': illegal_break_hours,
                'start_time': start_time,
                'end_time': end_time,
            }
        )
        if created:
            print(f"Created new record for {employee} on {date}.")
        else:
            print(f"Updated record for {employee} on {date}.")
    except Exception as e:
        print(f"Error saving work hours to DB: {e}")


from datetime import timedelta
from django.utils import timezone

def calculate_daily_work_hours(events, employee):
    debug_print = False
    if debug_print:
        print("\n\n----------------------------------------------------------------\n")
        print("This is calculate_daily_work_hours start.\n")

    daily_work_hours = {}
    daily_break_hours = {'legal': {}, 'illegal': {}}
    work_start_end_times = {}

    ongoing_work_period = None
    ongoing_break_period = None
    break_type = None

    for event in events:
        event_time = event.event_time

        # Ensure event_time is timezone-aware
        if timezone.is_naive(event_time):
            event_time = timezone.make_aware(event_time)

        date = event_time.date()

        # Initialize daily tracking if not already set
        if date not in daily_work_hours:
            daily_work_hours[date] = timedelta()
            work_start_end_times[date] = {'start': None, 'end': None}
            daily_break_hours['legal'][date] = timedelta()
            daily_break_hours['illegal'][date] = timedelta()

        # Process events by event_type
        if event.event_type == AttendanceEvent.EventType.WORK_START:
            ongoing_work_period = event_time
            work_start_end_times[date]['start'] = event_time

        elif event.event_type == AttendanceEvent.EventType.WORK_END and ongoing_work_period:
            work_duration = event_time - ongoing_work_period
            work_start_end_times[date]['end'] = event_time

            # Subtract ongoing break duration if any
            if ongoing_break_period:
                break_duration = event_time - ongoing_break_period
                break_type = (
                    'legal' if event.departure_reason == AttendanceEvent.DepartureReason.LEGAL else 'illegal'
                )
                daily_break_hours[break_type][date] += break_duration
                work_duration -= break_duration
                ongoing_break_period = None

            # Add work duration to the daily total
            daily_work_hours[date] += work_duration
            ongoing_work_period = None

        elif event.event_type == AttendanceEvent.EventType.BREAK_START:
            ongoing_break_period = event_time
            break_type = (
                'legal' if event.departure_reason == AttendanceEvent.DepartureReason.LEGAL else 'illegal'
            )

        elif event.event_type == AttendanceEvent.EventType.BREAK_END and ongoing_break_period:
            break_duration = event_time - ongoing_break_period
            daily_break_hours[break_type][date] += break_duration
            ongoing_break_period = None
            break_type = None

    # Convert timedelta to hours
    daily_work_hours_in_hours = convert_timedelta_to_hours(daily_work_hours)
    daily_break_hours_in_hours = {
        'legal': convert_timedelta_to_hours(daily_break_hours['legal']),
        'illegal': convert_timedelta_to_hours(daily_break_hours['illegal']),
    }

    # Debugging output
    if debug_print:
        print("\nDaily work hours:", daily_work_hours_in_hours)
        print("\nDaily break hours:", daily_break_hours_in_hours)

    # Save work hours to the database
    for date in daily_work_hours_in_hours:
        save_work_hours_to_db(
            employee,
            date,
            daily_work_hours_in_hours[date],
            daily_break_hours_in_hours['legal'].get(date, (0, 0))[0],
            daily_break_hours_in_hours['illegal'].get(date, (0, 0))[0],
            work_start_end_times[date]
        )

    return daily_work_hours_in_hours, daily_break_hours_in_hours, work_start_end_times


from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.utils.translation import gettext as _
from .models import WorkDay

# Used
def workdays_list(request):
    # Získání seznamu zaměstnanců, kteří mají přiřazené pracovní dny
    employees = Person.objects.filter(workday__isnull=False).distinct()
    
    # Získání filtrů z GET požadavku
    employee_unique_id = request.GET.get('employee')
    workday_date = request.GET.get('workday_date')  # Datum pracovního dne
    
    # Filtrujte pracovní dny podle parametrů
    workdays = WorkDay.objects.all()
    if employee_unique_id:
        workdays = workdays.filter(employee__unique_id=employee_unique_id)
    if workday_date:
        # Ověření a filtrování podle data
        parsed_date = parse_date(workday_date)
        if parsed_date:
            workdays = workdays.filter(date=parsed_date)

    # Seřaďte pracovní dny podle data
    workdays = workdays.order_by('date')  # Použijte '-' pro sestupné řazení

    return render(request, 'eval/workdays_list.html', {
        'workdays': workdays,
        'employees': employees,
        'title': _("Work Days List"),
    })



from django.shortcuts import render
from django.utils.dateparse import parse_date
from datetime import datetime
from .models import Person, WorkDay

def workdays_list_person_date(request, person_id, year, month):
    # Get the employee (Person) by person_id
    person = Person.objects.get(id=person_id)

    # Filter workdays by the person and the provided year and month
    workdays = WorkDay.objects.filter(employee=person)
    
    # Filter by year and month
    workdays = workdays.filter(date__year=year, date__month=month)

    # Optionally, you can sort the workdays by date
    workdays = workdays.order_by('date')

    # Get all employees for the dropdown
    employees = Person.objects.all()

    return render(request, 'eval/workdays_list.html', {
        'workdays': workdays,
        'employees': employees,
        'person': person,
        'year': year,
        'month': month,
        'title': _("Work Days List"),
    })


def workdays_and_summary(request, person_id):
    # Get the person details
    person = Person.objects.get(id=person_id)
    
    # Get the month from the form
    month = request.POST.get('month')
    action = request.POST.get('action')
    
    if action == 'view_summary':
        # Handle attendance summary for the selected month
        year, month = month.split('-')
        # Your logic to calculate the attendance summary for the selected month
        return redirect('eval:monthly_work_hours', person_id=person_id, year=year, month=month)
    
    elif action == 'view_workdays':
        # Handle workdays list for the selected month
        year, month = month.split('-')
        workdays = WorkDay.objects.filter(employee_id=person_id, date__year=year, date__month=month).order_by('date')
        
        return render(request, 'eval/workdays_list.html', {
            'workdays': workdays,
            'person': person,
            'title': _("Work Days List"),
        })

    # Default case if no action is selected
    return render(request, 'eval/person_detail.html', {
        'person': person,
        'title': _("Person Details"),
    })

def person_detail(request, employee_id, date):
    # Zpracování dat (např. načtení zaměstnance a detailů dne)
    context = {
        'employee_id': employee_id,
        'date': date,
    }
    return render(request, 'eval/person_detail.html', context)