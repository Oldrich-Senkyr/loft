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

