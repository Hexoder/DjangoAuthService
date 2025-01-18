from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from ..services.AuthService import AuthService


class AuthServiceAuthentication(BaseAuthentication):
    def __init__(self):
        ...

    def authenticate(self, request):
        """
        Authenticate the user using the custom AuthService.
        """
        authorization_header = request.headers.get("Authorization")

        if not authorization_header or not authorization_header.startswith("Bearer "):
            return None  # No authentication header, continue to next authentication class

        token = authorization_header.split("Bearer ")[1]
        auth_service = AuthService(token)
        try:
            # Use AuthService to validate the token and get the user
            user = auth_service.get_user_from_token(token)
            if not user:
                raise AuthenticationFailed("Invalid token: User not found")
            return (user, token)  # Return user and token as required by DRF
        except Exception as e:
            raise AuthenticationFailed(f"Authentication failed: {str(e)}")
