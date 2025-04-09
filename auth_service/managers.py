from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import FieldError
from .grpc_client.client import AuthClient

client = AuthClient()


class BaseAuthUserManager(BaseUserManager):

    def get(self, *args, **kwargs):
        try:
            user = super().get(*args, **kwargs)
            user_data = client.get_user_data(id=user.id)
        except FieldError:
            user_data = client.get_user_data(**kwargs)
            user = super().get(id=user_data.get("id"))

        if user and user_data:
            user.update_fields(user_data)
        return user

    def filter(self, *args, **kwargs):
        try:
            queryset = super().filter(*args, **kwargs)
        except FieldError:
            user_ids = client.filter_user(**kwargs).get("user_id", [])
            queryset = super().filter(id__in=user_ids)

        for obj in queryset:
            obj.reload_meta()
        return queryset

    def last(self):
        user = super().last()
        if user:
            user.reload_meta()
        return user

    def all(self):
        queryset = super().all()
        for obj in queryset:
            obj.reload_meta()
        return queryset

    def get_by_natural_key(self, national_id):
        return self.get(national_id=national_id)
