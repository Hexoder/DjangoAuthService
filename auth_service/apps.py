from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from auth_service.utils import get_user_model_from_string


class AuthServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_service'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        self.USER_DB_MODEL = False

    def ready(self):
        if not getattr(settings, 'USER_DB_MODEL', False):
            return

        required_variables = {
            "AUTH_USER_MODEL": getattr(settings, 'AUTH_USER_MODEL', None),
            "AUTH_TRUSTED_IP": getattr(settings, 'AUTH_TRUSTED_IP', None),
            "AUTH_TRUSTED_ORIGIN": getattr(settings, 'AUTH_TRUSTED_ORIGIN', None),
            "AUTH_SHARED_SECRET": getattr(settings, 'AUTH_SHARED_SECRET', None)
        }

        for var in required_variables:
            if not required_variables[var]:
                raise ImproperlyConfigured(f'You must define {var} in your settings')

        User = get_user_model_from_string(required_variables['AUTH_USER_MODEL'])

        from auth_service.models import BaseAuthUser

        if not issubclass(User, BaseAuthUser):
            raise ImproperlyConfigured(
                'Your custom AUTH_USER_MODEL must inherit from BaseAuthUser'
            )

        self.USER_DB_MODEL = True
