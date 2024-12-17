from django.db import models
from django.utils.translation import gettext_lazy as _
from agent.models import Person

class Project(models.Model):
    # Existing fields
    code = models.CharField(
        max_length=9,
        unique=True,
        null=False,
        verbose_name=_("Project Code"),
        help_text=_("Code of the project, e.g., 25R001, 25K001."),
    )
    name = models.CharField(
        max_length=70,
        verbose_name=_("Project Name")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Optional description of the project.")
    )

    # New fields
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Start Date"),
        help_text=_("Date when the project starts.")
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("End Date"),
        help_text=_("Date when the project is expected to end.")
    )

    planned_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Planned Hours"),
        help_text=_("Planned number of hours for the project.")
    )
    worked_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Worked Hours"),
        help_text=_("Worked number of hours on the project.")
    )
    status = models.IntegerField(
        choices=[
            (0, _('New')),
            (1, _('In Progress')),
            (2, _('Completed')),
            (3, _('Canceled')),
        ],
        default=0,
        verbose_name=_("Status"),
        help_text=_("Project status: 0 = new, 1 = in progress, 2 = completed, 3 = canceled.")
    )

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    def __str__(self):
        return f"{self.code} - {self.name}"


class PersonProject(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_("Person"))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=_("Project"))
    assigned_at = models.DateTimeField(auto_now=False, verbose_name=_("Assigned At"))
    role_in_project = models.CharField(max_length=50, verbose_name=_("Role in Project"))

    class Meta:
        verbose_name = _("Person-Project Assignment")
        verbose_name_plural = _("Person-Project Assignments")

    def __str__(self):
        return f"{self.person.last_name} - {self.project.code} ({self.role_in_project})"
    

from django.db import models
from django.utils.translation import gettext_lazy as _

class WorkLog(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_("Person"))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=_("Project"))
    work_date = models.DateField(verbose_name=_("Work Date"))
    hours_allocated = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name=_("Hours Allocated"),
        help_text=_("Number of hours allocated to the project on the given date.")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"), help_text=_("Description of the work done."))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Work Log")
        verbose_name_plural = _("Work Logs")

    def __str__(self):
        return _("Work log for {} on {} for project {}").format(self.person.last_name, self.work_date, self.project.code)
