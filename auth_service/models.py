from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import PermissionsMixin

from .managers import BaseAuthUserManager


class BaseAuthUser(AbstractBaseUser, PermissionsMixin):
    remote_fields = {"phone": None,
                     "email": None,
                     "first_name": None,
                     "last_name": None,
                     "service": {},
                     "sub_services": [],
                     "roles": [],
                     "departments": [],
                     "image": None,
                     "username": None,
                     "is_verified": None
                     }

    def exists_in_db(self):
        from django.contrib.auth import get_user_model
        CustomUser = get_user_model()
        return self.pk is not None and CustomUser.objects.filter(pk=self.pk).exists()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initiating base user model fields for CustomUser instances
        self.phone: str = ""
        self.email: str = ""
        self.first_name: str = ""
        self.last_name: str = ""
        self.service: dict[str:str] = {}
        self.sub_services: list[str] = []
        self.roles: list[str] = []
        self.departments: list[str] = []
        self.image: str = ""
        self.username: str = ""
        self.is_verified: bool = True

        if self.exists_in_db():
            self.reload_meta()

    id = models.PositiveIntegerField(primary_key=True, unique=True)
    national_id = models.CharField(max_length=10, null=True, blank=True, unique=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'national_id'

    objects = BaseAuthUserManager()

    class Meta:
        abstract = True

    def reload_meta(self):
        from .grpc_client.client import AuthClient
        client = AuthClient()
        try:
            user_data = client.get_user_data(id=int(self.id))
            self.update_fields(user_data)
        except Exception:
            ...
        return self

    def update_fields(self, fetched_user):

        if fetched_user:
            for k, v in fetched_user.items():
                match k:
                    case "national_id":
                        if not self.national_id or (self.national_id and self.national_id != v):
                            setattr(self, k, v)
                            self.save(update_fields=['national_id'])

                    case "is_superuser":
                        if not self.is_superuser or (self.is_superuser and self.is_superuser != v):
                            setattr(self, k, v)
                            self.save(update_fields=['is_superuser'])

                    case "is_staff":
                        if not self.is_staff or (self.is_staff and self.is_staff != v):
                            setattr(self, k, v)
                            self.save(update_fields=['is_staff'])
                    case _:
                        setattr(self, k, v)
                        self.save()

            return self
        else:
            return self


class User:
    def __init__(self, id, user_data):
        self.id = id
        self.is_authenticated = True
        for field_name, default_value in BaseAuthUser.remote_fields.items():
            setattr(self, field_name, user_data.get(field_name, default_value))
