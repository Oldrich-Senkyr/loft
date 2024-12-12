from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import AttendanceEvent
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.forms import DateTimeInput


class EventTimeFilter(admin.SimpleListFilter):
    title = _('event time')  # Filter title displayed in the admin interface
    parameter_name = 'event_time'  # The name of the parameter used in the URL

    def lookups(self, request, model_admin):
        # Choices that will be displayed in the filter options
        return (
            ('today', _('Today')),
            ('past_7_days', _('Past 7 days')),
            ('this_month', _('This month')),
            ('this_year', _('This year')),
            ('choose_date', _('Choose specific date')),  # Option for selecting a specific date
        )

    def queryset(self, request, queryset):
        if self.value() == 'today':
            return queryset.filter(event_time__date=datetime.today().date())
        elif self.value() == 'past_7_days':
            today = datetime.today()
            return queryset.filter(event_time__gte=today - timedelta(days=7))
        elif self.value() == 'this_month':
            today = datetime.today()
            return queryset.filter(event_time__month=today.month, event_time__year=today.year)
        elif self.value() == 'this_year':
            today = datetime.today()
            return queryset.filter(event_time__year=today.year)
        elif self.value() == 'choose_date':
            # Here we handle the custom date input
            date_param = request.GET.get('specific_date')
            if date_param:
                try:
                    specific_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                    return queryset.filter(event_time__date=specific_date)
                except ValueError:
                    pass
            return queryset
        return queryset

    def choices(self, changelist):
        choices = super().choices(changelist)
        return choices

# Custom form for the AttendanceEvent model
class AttendanceEventForm(forms.ModelForm):
    class Meta:
        model = AttendanceEvent
        fields = '__all__'  # Use all model fields in the form

    # Customizing the widget for event_time field to allow datetime input
    event_time = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local'}),
        required=True,
    )

# Admin class for managing AttendanceEvent in the admin interface
class AttendanceEventAdmin(admin.ModelAdmin):
    form = AttendanceEventForm
    list_display = ('person', 'event_type', 'event_time', 'departure_reason', 'timestamp')
    search_fields = ('person__name', 'event_type', 'event_time', 'departure_reason')  # Search across multiple fields
    list_filter = ('person', EventTimeFilter)  # Custom filter added for event_time

admin.site.register(AttendanceEvent, AttendanceEventAdmin)
