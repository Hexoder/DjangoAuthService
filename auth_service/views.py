from django.core.management import call_command
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
import json
from django.conf import settings


class SystemPermission(BasePermission):
    """
    Allows access only to a specific internal IP, origin header, and password.
    """

    TRUSTED_IP = settings['AUTH_TRUSTED_IP']
    TRUSTED_ORIGIN = settings['AUTH_TRUSTED_ORIGIN']
    SHARED_SECRET = settings['AUTH_SHARED_SECRET']

    def has_permission(self, request, view):
        # Extract real client IP (supporting X-Forwarded-For if behind proxy)
        ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
        client_ip = ip.split(",")[0].strip()

        if client_ip != self.TRUSTED_IP:
            print(f"❌ Rejected IP: {client_ip}")
            return False

        # Extract origin header
        origin = request.META.get("HTTP_X_SERVICE_ORIGIN")
        if origin != self.TRUSTED_ORIGIN:
            print(f"❌ Invalid origin header: {origin}")
            return False

        # Validate password
        try:
            body = json.loads(request.body.decode())
            password = body.get("password")
        except Exception as e:
            print(f"❌ Failed to parse JSON body: {e}")
            return False

        if password != self.SHARED_SECRET:
            print("❌ Invalid shared secret")
            return False

        print("✅ Request passed all permission checks")
        return True


class UpdateUserSignalApiView(APIView):
    permission_classes = [SystemPermission]

    def post(self, request):
        call_command('sync_users_from_grpc')
        return Response("DONE", status=status.HTTP_200_OK)
