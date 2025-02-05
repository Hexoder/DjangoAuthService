import requests
import jwt
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied

class AuthService:
    """
    A service class to interact with the external authentication service.
    Handles user fetching (single and bulk) with optional caching.
    """

    AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL
    AUTH_SERVICE_BULK_URL = "http://auth-service-domain/api/users/bulk/"
    CACHE_TIMEOUT = settings.USER_DATA_TIMEOUT
    SERVICE_NAME = settings.SERVICE_NAME
    def __init__(self, token):
        """
        Initialize the AuthService with the user's JWT token.
        """
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.jwt_secret = settings.SECRET_KEY
        self.jwt_algorithm = "HS256"

    def get_user_from_token(self, token):
        try:
            decoded_payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = decoded_payload.get("user_id")
            if not user_id:
                raise PermissionDenied("Invalid token: user_id not found")
            return self._convert_user_dict_to_object(self.fetch_user(user_id))
        except jwt.ExpiredSignatureError:
            raise PermissionDenied("Token has expired")
        except jwt.InvalidTokenError:
            raise PermissionDenied("Invalid token")

    def fetch_user(self, user_id):
        """
        Fetch a single user's details from the Auth Service with caching.
        """
        cache_key = f"user_id_{user_id}"
        user = cache.get(cache_key)
        if not user:
            response = requests.get(f"{self.AUTH_SERVICE_URL}users/{user_id}/", headers=self.headers)
            if response.status_code == 200:
                user = response.json()
                cache.set(cache_key, user, timeout=self.CACHE_TIMEOUT)
            else:
                self._handle_error(response)

        return user

    def fetch_users_in_bulk(self, user_ids):
        """
        Fetch multiple users' details from the Auth Service with caching.
        """
        user_details = {}
        uncached_user_ids = []

        for user_id in user_ids:
            cache_key = f"user_id_{user_id}"
            user = cache.get(cache_key)
            if user:
                user_details[user_id] = user
            else:
                uncached_user_ids.append(user_id)

        if uncached_user_ids:
            response = requests.post(
                self.AUTH_SERVICE_BULK_URL,
                json={"user_ids": uncached_user_ids},
                headers=self.headers
            )

            if response.status_code == 200:
                fetched_users = response.json()
                for user in fetched_users:
                    cache_key = f"user_id_{user['id']}"
                    cache.set(cache_key, user, timeout=self.CACHE_TIMEOUT)  # Cache each user
                    user_details[user["id"]] = user
            else:
                self._handle_error(response)

        return user_details

    def invalidate_user_cache(self, user_id):
        """
        Invalidate the cache for a single user.
        """
        cache_key = f"user_id_{user_id}"
        cache.delete(cache_key)

    def invalidate_bulk_cache(self, user_ids):
        """
        Invalidate the cache for multiple users.
        """
        for user_id in user_ids:
            self.invalidate_user_cache(user_id)

    def _handle_error(self, response):
        """
        Handle errors from the Auth Service API.
        """
        if response.status_code == 401:
            raise Exception("Unauthorized: Token is invalid or expired")
        elif response.status_code == 404:
            raise Exception("User not found")
        else:
            raise Exception(f"Auth Service Error: {response.status_code} - {response.text}")

    @staticmethod
    def _convert_user_dict_to_object(user_data: dict):
        """
        Convert a user dictionary to a simple object with attributes.
        """
        if not user_data:
            return None

        class User:
            def __init__(self, user_data):
                self.id = user_data.get("id")
                self.national_id = user_data.get("national_id")
                self.username = user_data.get("username", None)
                self.email = user_data.get("email", None)
                self.roles = user_data.get("roles", [])
                self.departments = user_data.get("departments", [])
                self.service = user_data.get("service", {})
                self.sub_services = user_data.get("sub_services", [])
                self.is_authenticated = True

        return User(user_data)

    def get_marketers(self):
        response = requests.get(f"{self.AUTH_SERVICE_URL}marketers/", headers=self.headers)
        return response.json()
    
    def get_marketer(self, national_id):
        response = requests.get(f"{self.AUTH_SERVICE_URL}marketers/{national_id}", headers=self.headers)
        return response.json(), response.status_code 
    
    def update_marketer(self, payload, national_id):
        response = requests.patch(f"{self.AUTH_SERVICE_URL}marketers/{national_id}/", headers=self.headers,data=payload)
        return response.json(), response.status_code
    
    def create_marketer(self, payload):
        response = requests.post(f"{self.AUTH_SERVICE_URL}marketers/", headers=self.headers, data=payload)
        return response.json(), response.status_code

    def check_marketer_exist(self, national_id):
        response = requests.get(f"{self.AUTH_SERVICE_URL}check-marketer/{national_id}/", headers=self.headers)
        return response

