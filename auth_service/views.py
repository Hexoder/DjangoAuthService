from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from auth_service.serializers import SignalSerializer


class UpdateUserSignalApiView(APIView):

    def post(self, request):
        serializer = SignalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
