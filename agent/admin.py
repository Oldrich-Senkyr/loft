from django.contrib import admin
from .models import Person, Company, Division, Team, Employee
from django.utils.translation import gettext_lazy as _

class PersonAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'first_name', 'last_name', 'get_role_display']
    fieldsets = (
        (None, {
            'fields': ('display_name', 'first_name', 'last_name', 'role', 'title_before', 'title_after')
        }),
    )

    def get_fieldsets(self, request, obj=None):
        # Použití překladu pro názvy polí přímo v Adminu
        fieldsets = super().get_fieldsets(request, obj)
        return fieldsets

admin.site.register(Person, PersonAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AppUser  # Import vašeho modelu

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import AppUser

@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    # Zobrazené pole v seznamu uživatelů
    list_display = ('username', 'email', 'first_name', 'last_name', 'position', 'is_staff', 'is_active')
    list_filter = ('position', 'is_staff', 'is_active', 'is_superuser', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    # Konfigurace formulářů pro zobrazení detailů uživatele
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Additional info'), {'fields': ('position', )}),
    )
    # Konfigurace formuláře pro přidání nového uživatele
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'position'),
        }),
    )



from django.contrib import admin
from .models import Company, Division, Team, Employee

# Company Admin
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'get_leader_info')

    def get_leader_info(self, obj):
        if obj.leader and obj.leader.user:  # Check if both are not None
            return f"{obj.leader.user.username} ({obj.leader.role})"
        else:
            return "No Leader Assigned"
    
    get_leader_info.short_description = "Leader Information"

admin.site.register(Division, DivisionAdmin)



# Team Admin
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'division', 'get_leader')

    def get_leader(self, obj):
        if obj.leader:
            return f"{obj.leader.user.username} ({obj.leader.role})"
        return "No Leader Assigned"
    get_leader.short_description = "Team Leader"


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'get_full_name', 'employee_role', 'get_division', 'get_team')
    fields = ('user', 'first_name', 'last_name', 'employee_role', 'team')  # Zahrnuje pole pro uživatele a tým

    def get_user_name(self, obj):
        """
        Vrací uživatelské jméno propojeného uživatele nebo informaci, že uživatel není přiřazen.
        """
        if obj.user:  # Kontrola, zda je user nastaven
            return obj.user.username
        return "No User Assigned"
    get_user_name.short_description = "User Name"

    def get_full_name(self, obj):
        """
        Vrací celé jméno zaměstnance.
        """
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = "Full Name"

    def get_division(self, obj):
        """
        Vrací jméno divize, pokud zaměstnanec patří do týmu, který je přiřazen k divizi.
        """
        if obj.team and obj.team.division:
            return obj.team.division.name
        return "No Division Assigned"
    get_division.short_description = "Division"

    def get_team(self, obj):
        """
        Vrací jméno týmu, pokud je zaměstnanec členem týmu.
        """
        if obj.team:
            return obj.team.name
        return "No Team Assigned"
    get_team.short_description = "Team"
