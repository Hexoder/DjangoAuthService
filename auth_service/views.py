from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from auth_service.serializers import SignalSerializer
from django.core.management import call_command


# Run a built-in command, like migrate

class UpdateUserSignalApiView(APIView):

    def post(self, request):
        # serializer = SignalSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_200_OK)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        call_command('sync_users_from_grpc')
        return Response("DONE", status=status.HTTP_200_OK)
