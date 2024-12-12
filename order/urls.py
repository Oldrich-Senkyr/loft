from django.urls import path
from order.views import workday_assignments

app_name = 'order'

urlpatterns = [
    path('workday/<int:employee_id>/<str:date>/', workday_assignments, name='workday_assignments'),
]
