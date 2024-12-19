from django.contrib import admin
from .models import Person
from django.utils.translation import gettext_lazy as _

class PersonAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'first_name', 'last_name', 'organization', 'get_role_display']
    fieldsets = (
        (None, {
            'fields': ('display_name', 'first_name', 'last_name', 'organization', 'role', 'title_before', 'title_after')
        }),
    )

    def get_fieldsets(self, request, obj=None):
        # Použití překladu pro názvy polí přímo v Adminu
        fieldsets = super().get_fieldsets(request, obj)
        return fieldsets

admin.site.register(Person, PersonAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser  # Import vašeho modelu

class CustomUserAdmin(UserAdmin):
    # Zobrazené pole v admin rozhraní
    list_display = ('username', 'email', 'position', 'is_staff', 'is_active')
    list_filter = ('position', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    # Konfigurace formulářů pro zobrazení detailů uživatele
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Additional info'), {'fields': ('position', 'divisions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'position'),
        }),
    )

# Registrace modelu do administrace
admin.site.register(CustomUser, CustomUserAdmin)


