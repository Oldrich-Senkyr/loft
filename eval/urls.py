from django.urls import path
from eval.views import attendance_events_by_person_and_date, monthly_work_hours, attendance_summary_view, workdays_list
from eval.views import workdays_list_person_date, workdays_and_summary,person_detail
app_name = 'eval'

urlpatterns = [
    path('attendance-events/<int:person_id>/<str:date>/', attendance_events_by_person_and_date, name='attendance_events_by_person_and_date'),
    path('attendance/monthly-summary/detail/<int:person_id>/<int:year>/<int:month>/', monthly_work_hours, name='monthly_work_hours'),
    path("attendance/monthly-summary/summary/<int:person_id>/", attendance_summary_view, name="attendance_summary"),
    path('workdays-list/', workdays_list, name='workdays_list'),
    path('workdays-list-person-date/<int:person_id>/<int:year>/<int:month>/', workdays_list_person_date, name='workdays_list_person_date'),
     # New combined view for both functionalities
    path('person/<int:person_id>/', workdays_and_summary, name='workdays_and_summary'),
    
    path('person/<int:employee_id>/<str:date>/', person_detail, name='person_detail'),
    
]




