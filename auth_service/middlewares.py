# from django.utils.functional import SimpleLazyObject
# from django.core.exceptions import MiddlewareNotUsed
# from django.conf import settings
# from .services.Authentication import AuthService
#
#
# class AuthServiceMiddleware:
#     """
#     Middleware for authenticating users via the AuthService.
#     Adds the authenticated user object to the request.
#     """
#
#     def __init__(self, get_response):
#         self.get_response = get_response
#         self.auth_service_enabled = getattr(settings, "AUTH_SERVICE_ENABLED", True)
#
#         if not self.auth_service_enabled:
#             raise MiddlewareNotUsed("AuthServiceMiddleware is disabled in settings.")
#
#     def __call__(self, request):
#         request.user = self.get_authenticated_user(request)
#         response = self.get_response(request)
#         return response
#
#     def get_authenticated_user(self, request):
#         """
#         Fetch and authenticate the user using AuthService.
#         """
#         authorization_header = request.headers.get("Authorization")
#         if not authorization_header or not authorization_header.startswith("Bearer "):
#             return None
#
#         token = authorization_header.split("Bearer ")[1]
#         authenticator = AuthService(token=token)
#         try:
#             print('authenticating')
#             user, token = authenticator.authenticate()

#             return user
#         except Exception as e:
#             # Handle token errors or auth service errors
#             print(f"AuthService Error: {e}")
#             return None
