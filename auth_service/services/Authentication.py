from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from ..grpc_client.client import AuthClient
from ..utils import is_user_db_model


class AuthService:
    def __init__(self, token):
        self.client = AuthClient()
        self.token = token

    def _user_model_authenticate(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            result = self.client.verify_login(self.token)
            user_id = result.get('user_id')
            user, created = User.objects.get_or_create(id=int(user_id))
            return user, self.token,
        except Exception as err:
            err.__dict__.update({'msg': "Authentication failed"})
            raise AuthenticationFailed(err.__dict__)

    def _non_user_model_authenticate(self):
        from ..models import User

        try:
            result = self.client.verify_login(self.token)
            user_id = result.get('user_id')
            user_data = self.client.get_user_data(id=int(user_id))

            user = User(id=int(user_id), user_data=user_data)

            return user, self.token,
        except Exception as err:
            raise AuthenticationFailed(f"Authentication failed: {str(err)}")

    def authenticate(self):
        if is_user_db_model():
            return self._user_model_authenticate()
        else:
            return self._non_user_model_authenticate()


class AuthServiceDrfAuthentication(BaseAuthentication):

    def authenticate(self, request):
        authorization_header = request.headers.get("Authorization")

        if not authorization_header or not authorization_header.startswith("Bearer "):
            return None  # No authentication header, continue to next authentication class

        token = authorization_header.split("Bearer ")[1]

        authenticator = AuthService(token=token)
        print('authenticating')

        return authenticator.authenticate()
