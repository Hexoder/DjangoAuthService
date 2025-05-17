from rest_framework import serializers
from django.contrib.auth import get_user_model
from auth_service.grpc_client.client import AuthClient

CustomUser = get_user_model()
client = AuthClient()


class BaseSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        excluded_fields = kwargs.pop('excluded_fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if excluded_fields is not None:
            all_fields = set(self.fields.keys())
            disallowed = set(excluded_fields)
            for field_name in all_fields.intersection(disallowed):
                self.fields.pop(field_name)

    class Meta:
        model = None  # You need to set this in the derived serializers
        fields = '__all__'


class UserSerializer(BaseSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'national_id', 'contacts']

    def get_fields(self):
        fields = super().get_fields()
        model = self.Meta.model

        # Add dynamic fields from the model's `remote_fields`
        if hasattr(model, 'remote_fields'):
            for field_name in model.remote_fields:
                # Use the correct field type (adjust as needed)
                fields[field_name] = serializers.CharField(read_only=True)

        return fields

class SignalSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)

    @staticmethod
    def validate_id(value):
        if CustomUser.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"user with id {value} already exists!")

        return value

    def create(self, validated_data):
        try:
            user_id = validated_data.get('id')
            user_data = client.get_user_data(id=user_id)
            user = CustomUser.objects.create(id=user_id)
            return user
        except Exception as err:
            res = serializers.ValidationError(err.dict)
            res.status_code = 404
            raise res