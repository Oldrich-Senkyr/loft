# Create your models here.
from django.db import models
from django.contrib.auth.models import User  # Nebo vlastní model zaměstnance
from django.utils.translation import gettext_lazy as _
from agent.models import Person

from django.db import models

from agent.models import Person
from order.models import Project
from datetime import timedelta





from django.db import models
from django.utils.translation import gettext_lazy as _

class WorkDay(models.Model):
    employee = models.ForeignKey(
        Person,  # Předpokládám, že máte model Person
        on_delete=models.CASCADE, 
        verbose_name=_("Employee")
    )
    date = models.DateField(verbose_name=_("Date"))
    
    start_time = models.TimeField(
        verbose_name=_("Start Time"),
        null=True, 
        blank=True,
        help_text=_("Time when the employee started work.")
    )
    end_time = models.TimeField(
        verbose_name=_("End Time"),
        null=True, 
        blank=True,
        help_text=_("Time when the employee finished work.")
    )
    
    total_work_hours = models.DurationField(
        verbose_name=_("Total Work Hours"),
        help_text=_("Total work hours including breaks and working time.")
    )
    
    total_legal_break = models.DurationField(
        verbose_name=_("Total Legal Break Hours"),
        default=timedelta(),
        help_text=_("Total time for legal breaks.")
    )
    
    total_illegal_break = models.DurationField(
        verbose_name=_("Total Illegal Break Hours"),
        default=timedelta(),
        help_text=_("Total time for unauthorized breaks.")
    )
    
    assigned_hours = models.DurationField(
        verbose_name=_("Assigned Hours"),
        default=timedelta(),
        help_text=_("Total time for assigned hours.")
    )
    
    class Meta:
        unique_together = ('employee', 'date')
        verbose_name = _("Work Day")
        verbose_name_plural = _("Work Days")
    
    def __str__(self):
        return f"{self.employee} - {self.date} - {self.total_work_hours}"

class WorkDayAssignment(models.Model):
    workday = models.ForeignKey(
        WorkDay,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name=_("Work Day"),
        help_text=_("The workday to which this assignment belongs."),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_("Project"),
        help_text=_("The project to which the hours are assigned."),
    )
    assigned_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Assigned Hours"),
        help_text=_("The number of hours assigned to this project."),
    )
    work_performed = models.CharField(
        max_length=100,
        verbose_name=_("Work Performed"),
        help_text=_("Description of the work performed."),
    )

    class Meta:
        unique_together = ('workday', 'project')
        verbose_name = _("Work Day Assignment")
        verbose_name_plural = _("Work Day Assignments")

    def __str__(self):
        return f"{self.workday} - {self.project} - {self.assigned_hours} hours"
