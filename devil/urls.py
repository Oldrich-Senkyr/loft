from django.urls import path
from .views import show_session_data
from devil.views import show_session_data
from devil.attendance_views.views import create_attendance_event

app_name = 'devil'

urlpatterns = [
    path('show-session-data/',show_session_data, name='show_session_data'),
    path("attendance-event/new/", create_attendance_event, name="create_attendance_event"),
]




