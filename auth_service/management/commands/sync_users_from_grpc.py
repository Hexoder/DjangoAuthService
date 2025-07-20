from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import connection


class Command(BaseCommand):
    help = 'Sync users from gRPC server'

    def handle(self, *args, **options):
        if not getattr(settings, 'USER_DB_MODEL', False):
            self.stdout.write(self.style.WARNING("USER_DB_MODEL is disabled."))
            return

        if settings.AUTH_USER_MODEL == 'auth.User':
            raise Exception('You must define a custom AUTH_USER_MODEL inheriting BaseAuthUser...')

        User = get_user_model()
        user_table = User._meta.db_table
        custom_user_model_name = getattr(settings, 'AUTH_USER_MODEL', None)
        custom_user_model_table = custom_user_model_name.lower().replace('.', '_')

        existing_tables = connection.introspection.table_names()

        if user_table not in existing_tables and custom_user_model_table not in existing_tables:
            self.stdout.write(self.style.ERROR(f"User table `{custom_user_model_table}` does not exist."))
            self.stdout.write(self.style.WARNING("run the migrations first!"))

            return

        try:
            from auth_service.grpc_client.client import AuthClient
            client = AuthClient()
            user_ids = client.filter_user().get('user_id')
            new_user_ids = set(map(int, user_ids))
            existing_user_ids = set(User.objects.values_list('id', flat=True))
            diff = new_user_ids.difference(existing_user_ids)
            reversed_diff = existing_user_ids.difference(new_user_ids)
            for user_id in diff:
                User.objects.create(id=user_id)

            User.objects.filter(id__in=reversed_diff).delete()

            self.stdout.write(self.style.SUCCESS(f"{len(diff)} new users synced."))
            self.stdout.write(self.style.SUCCESS(f"{len(reversed_diff)} old users deleted."))

        except Exception as err:
            self.stderr.write("Error fetching users: " + str(err))
