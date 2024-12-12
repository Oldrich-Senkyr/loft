from django.db import models
from django.utils import timezone
from datetime import datetime
from agent.models import Person
from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _

class AttendanceEvent(models.Model):
    class EventType(models.IntegerChoices):
        WORK_START = 1, _("Start of working hours")
        WORK_END = 2, _("End of working hours")
        BREAK_START = 3, _("Break start")
        BREAK_END = 4, _("Break end")
        VISIT_START = 5, _("Visit start")
        VISIT_END = 6, _("Visit end")

    class DepartureReason(models.IntegerChoices):
        NONE = 0, _("N/a")
        LEGAL = 1, _("Legal")
        ILLEGAL = 2, _("Illegal")

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="attendance_events")
    event_type = models.IntegerField(choices=EventType.choices)
    event_time = models.DateTimeField(default=timezone.now)
    timestamp = models.DateTimeField(default=timezone.now)
    departure_reason = models.IntegerField(choices=DepartureReason.choices, null=False, default=0,)

    def save(self, *args, **kwargs):
        # Clear departure reason if not applicable ............................................

        if self.departure_reason == None: 
            self.departure_reason =  AttendanceEvent.DepartureReason.NONE
           
        if self.event_type in {self.EventType.BREAK_START, self.EventType.VISIT_START} and self.departure_reason ==  AttendanceEvent.DepartureReason.NONE:
            self.departure_reason = AttendanceEvent.DepartureReason.ILLEGAL

        if self.event_type in {self.EventType.WORK_START, self.EventType.WORK_END, self.EventType.BREAK_END, self.EventType.VISIT_END}:
            self.departure_reason = AttendanceEvent.DepartureReason.NONE


        # Zajistíme, že pro daného zaměstnance a datum může být jen jeden "arrival"
        print(f"Event type: {self.event_type}")  # Prints the raw integer value
        print(f"event_time as string: {self.event_time}")
        # If event_time is a string, convert it to datetime
        if isinstance(self.event_time, str):
            try:
                # If event_time is a string, convert to datetime object
                self.event_time = datetime.strptime(self.event_time, "%Y-%m-%dT%H:%M")  # Adjust format as needed
            except ValueError:
                raise ValidationError(_("Invalid date/time format for event_time."))
        # Ensure event_time is aware if it is naive
        if timezone.is_naive(self.event_time):
            self.event_time = timezone.make_aware(self.event_time)

        
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.person} - {self.get_event_type_display()} - {self.event_time}"

    class Meta:
        verbose_name = _("Attendance Event")
        verbose_name_plural = _("Attendance Events")

