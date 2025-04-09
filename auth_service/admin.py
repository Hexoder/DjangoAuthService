from django.contrib import admin
from .utils import is_user_db_model


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'national_id']
    fieldsets = (
        (None, {
            'fields': (
                'national_id', 'is_staff', 'is_superuser')
        }),
    )
    readonly_fields = ['national_id', 'is_staff', 'is_superuser']


if is_user_db_model():
    from django.contrib.auth import get_user_model
    CustomUser = get_user_model()

    admin.site.register(CustomUser, CustomUserAdmin)
