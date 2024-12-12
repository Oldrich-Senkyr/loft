from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)  # Returns 0 if the key doesn't exist


@register.filter
def format_time(value):
    """
    Converts a tuple (hours, minutes) into a string formatted as 'X hours Y minutes'.
    """
    if isinstance(value, tuple) and len(value) == 2:
        hours, minutes = value
        # Format the time as HH:MM
        return f"{int(hours):02}:{int(minutes):02}"
    return value

# In your app's templatetags/custom_filters.py
from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def format_timedelta(value):
    if isinstance(value, timedelta):
        total_seconds = value.total_seconds()
        
        # Calculate the total hours and minutes
        total_hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        # Format hours: 2 digits if under 100, 3 digits if over 100
        if total_hours >= 100:
            return f"{int(total_hours):03}:{int(minutes):02}"
        else:
            return f"{int(total_hours):02}:{int(minutes):02}"
    return value
