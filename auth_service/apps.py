from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model
from .grpc_client.client import AuthClient


client = AuthClient()

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
            try:
                user_ids = client.filter_user().get('user_id')
                User = get_user_model()
                new_user_ids = set(map(int, user_ids))
                existing_user_ids = set(User.objects.values_list('id', flat=True))
                diff = new_user_ids.difference(existing_user_ids)
                for user_id in diff:
                    User.objects.create(id=int(user_id))
            except Exception as err:
                print("error fetching users, " + str(err))
