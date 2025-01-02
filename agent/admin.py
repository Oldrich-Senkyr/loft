from django.contrib import admin
from .models import Person, Company, Division, Team
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from .models import AppUser  # Import vašeho modelu


class PersonAdmin(admin.ModelAdmin):
    list_display = ['unique_id','display_name', 'first_name', 'last_name', 'get_role_display']
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






# Company Admin
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'get_leader_info')

    def get_leader_info(self, obj):
        if obj.leader:  # Check if both are not None
            return f"{obj.leader.last_name} {obj.leader.first_name}"
        else:
            return "No Leader Assigned"
    
    get_leader_info.short_description = "Leader Information"

admin.site.register(Division, DivisionAdmin)







# Registering Team for better management
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'division', 'get_leader', 'get_member_count')
    search_fields = ('name', 'division__name', 'leader__first_name', 'leader__last_name')
    list_filter = ('division',)

    def get_leader(self, obj):
        if obj.leader:
            return f"{obj.leader.last_name} {obj.leader.first_name}"
        return "No Leader Assigned"
    get_leader.short_description = "Team Leader"

    def get_member_count(self, obj):
        # Calculates the number of members in the team
        return obj.count()
    get_member_count.short_description = "Number of Members"


