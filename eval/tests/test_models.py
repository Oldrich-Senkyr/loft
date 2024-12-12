# myapp/tests/test_models.py

from django.test import TestCase
from agent.models import Person
from reader.models import AttendanceEvent
from django.utils import timezone
from datetime import timedelta
from eval.views import calculate_daily_work_hours

class CalculateDailyWorkHoursTestCase(TestCase):
    def setUp(self):
        # Vytvoření osoby
        self.person = Person.objects.create(name="Test Person", role="employee")
        
        # Vytvoření pracovních událostí pro tuto osobu
        self.event_start = AttendanceEvent.objects.create(
            person=self.person,
            event_type="work_start",
            timestamp=timezone.now() - timedelta(hours=1)
        )
        self.event_end = AttendanceEvent.objects.create(
            person=self.person,
            event_type="work_end",
            timestamp=timezone.now()
        )
    
    def test_calculate_daily_work_hours(self):
        # Ověření správného výpočtu pracovních hodin
        total_time = calculate_daily_work_hours(self.person)
        self.assertEqual(total_time, timedelta(hours=1))
