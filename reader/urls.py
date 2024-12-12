from django.urls import path
from .views import receive_event, add_attendance_event, events_list, event_detail, edit_attendance_event
from .views import select_person_and_date, delete_event, create_attendance_event
app_name = 'reader'

urlpatterns = [
    path('receive_event/',receive_event, name='receive_event'),
    path('add-attendance-event/', add_attendance_event, name='add_attendance_event'),
    path('events-list/', events_list, name='events_list'),
    path('event_detail/<int:event_id>/', event_detail, name='event_detail'),
    path('edit-attendance-event/<int:event_id>/', edit_attendance_event, name='edit_attendance_event'),
    path('select_person_and_date/', select_person_and_date, name='select_person_and_date'),
    path('delete-event/<int:event_id>/', delete_event, name='delete_event'),
    path('create_attendance_event/', create_attendance_event, name='create_attendance_event'),
]



