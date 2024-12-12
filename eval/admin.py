from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Project, WorkDay, WorkDayAssignment


class WorkDayAssignmentInline(admin.TabularInline):
    model = WorkDayAssignment
    extra = 1  # Počet prázdných řádků pro přidání nových záznamů
    verbose_name = _("Work Day Assignment")
    verbose_name_plural = _("Work Day Assignments")


@admin.register(WorkDay)
class WorkDayAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'start_time','end_time','total_work_hours', 'total_legal_break', 'total_illegal_break')
    list_filter = ('employee', 'date')
    search_fields = ('employee__username',)
    ordering = ('-date', 'employee')
    inlines = [WorkDayAssignmentInline]  # Inline pro správu přiřazení
    verbose_name = _("Work Day")
    verbose_name_plural = _("Work Days")




@admin.register(WorkDayAssignment)
class WorkDayAssignmentAdmin(admin.ModelAdmin):
    list_display = ('workday', 'project', 'assigned_hours')
    list_filter = ('workday__employee', 'project')
    search_fields = ('workday__employee__username', 'project__name')
    ordering = ('workday', 'project')
    verbose_name = _("Work Day Assignment")
    verbose_name_plural = _("Work Day Assignments")
