from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Project, PersonProject, WorkLog

# Registrace modelu Project v admin rozhraní
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # Určení, které sloupce se zobrazí v přehledu
    list_display = ('code', 'name', 'status', 'start_date', 'end_date', 'planned_hours', 'worked_hours')

    # Možnost hledání podle kódu a názvu
    search_fields = ('code', 'name')

    # Filtrování podle statusu
    list_filter = ('status',)

    # Určení výchozího řazení
    ordering = ('code',)

    # Možnost úpravy pořadí polí při přidávání nebo úpravě projektu
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'description')
        }),
        (_('Hours Information'), {
            'fields': ('planned_hours', 'worked_hours')
        }),
        (_('Date Information'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Status Information'), {
            'fields': ('status',)
        }),
    )

# Registrace modelu PersonProject
class PersonProjectAdmin(admin.ModelAdmin):
    list_display = ('person', 'project', 'role_in_project', 'assigned_at')
    search_fields = ('person__name', 'project__code', 'role_in_project')
    list_filter = ('assigned_at', 'role_in_project')
    ordering = ('assigned_at',)
    fieldsets = (
        (None, {
            'fields': ('person', 'project')
        }),
        (_('Role Information'), {
            'fields': ('role_in_project', 'assigned_at')
        }),
    )

admin.site.register(PersonProject, PersonProjectAdmin)

# Registrace modelu WorkLog
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ('person', 'project', 'work_date', 'hours_allocated', 'created_at', 'updated_at')
    search_fields = ('person__name', 'project__code', 'description')
    list_filter = ('work_date', 'hours_allocated')
    ordering = ('-work_date',)
    # Pouze pro zobrazení (nelze editovat)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('person', 'project', 'work_date')
        }),
        (_('Work Information'), {
            'fields': ('hours_allocated', 'description')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

admin.site.register(WorkLog, WorkLogAdmin)
