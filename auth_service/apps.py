from django.apps import AppConfig
from django.conf import settings


class AuthServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_service'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        self.USER_DB_MODEL = False

    def ready(self):
        DB_USER_MODEL = getattr(settings, 'USER_DB_MODEL', False)
        if DB_USER_MODEL:
            if settings.AUTH_USER_MODEL == 'auth.User':
                raise Exception('You must define a custom AUTH_USER_MODEL inheriting BaseAuthUser...')
            self.USER_DB_MODEL = True
