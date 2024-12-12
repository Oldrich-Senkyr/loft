# forms.py
from django import forms
from .models import AttendanceEvent
from django.utils import timezone
from django.utils.translation import gettext_lazy as _  # Import for translation

class AttendanceEventForm(forms.ModelForm):
    class Meta:
        model = AttendanceEvent
        fields = ['person', 'event_type', 'event_time', 'departure_reason']
        labels = {
            'person': _('Person'),
            'event_type': _('Event Type'),
            'event_time': _('Event Date and Time'),  # Změněno na "Event Date and Time"
            'departure_reason': _('Departure Reason'),
        }
        widgets = {
            'event_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'required': 'required'}),
        }
    
    # Validace pole event_time
    def clean_event_time(self):
        event_time = self.cleaned_data.get('event_time')
        print(f"cleaned event_time: {event_time}")  # Přidejte tento výstup pro kontrolu
        if not event_time:
            raise forms.ValidationError(_('Event time is required.'))
        # Povolit zadání minulého času pro opravy, ale pokud chcete nějaký jiný případ:
        # if event_time and event_time < timezone.now():
        #     raise forms.ValidationError(_('Event time cannot be in the past.'))
        return event_time

    # Můžete přidat metodu pro nastavení výchozího data na dnešek
   # def __init__(self, *args, **kwargs):
   #     person = kwargs.get('initial', {}).get('person')
   #     if person:
   #         # Přednastavíme `event_time` na dnešní den pro danou osobu
   #         kwargs['initial']['event_time'] = timezone.now().strftime('%Y-%m-%dT%H:%M')
   #     super().__init__(*args, **kwargs)
