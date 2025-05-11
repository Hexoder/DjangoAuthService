from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status


class SignalSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)

    def save(self, **kwargs):
        return super().save(**kwargs)


class UpdateUserSignalApiView(APIView):

    def post(self, request):
        serializer = SignalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
