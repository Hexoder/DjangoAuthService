import grpc
from . import auth_pb2, auth_pb2_grpc
from threading import Lock
from google.protobuf.json_format import MessageToDict
from django.conf import settings
from django.core.cache import cache


def get_secure_channel(server_domain):
    cert_path = 'authservice.pem'

    # Load server certificate
    with open(cert_path, "rb") as f:
        trusted_certs = f.read()

    # Create SSL/TLS credentials
    credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)

    # Create a secure channel
    return grpc.secure_channel(f"{server_domain}:50051", credentials)


def try_except(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result

        except grpc.RpcError as e:
            error_message = f"Error: {e.code()} - {e.details()}"
            print(error_message)

        except Exception as err:
            print(err)

    return wrapper


class AuthClient:
    _instance = None
    _lock = Lock()
    _service_name = None
    _sub_service_name = None
    _conn_address = None

    def __new__(cls):
        server_address = getattr(settings, "AUTH_GRPC_ADDRESS", "localhost")
        service_name = getattr(settings, "SERVICE_NAME", None)
        sub_service_name = getattr(settings, "SUB_SERVICE_NAME", None)

        if not server_address:
            raise Exception("Define AUTH_GRPC_ADDRESS in django settings")
        if not service_name:
            raise Exception("Define SERVICE_NAME in django settings")
        if not sub_service_name:
            raise Exception("Define SUB_SERVICE_NAME in django settings")

        cls._service_name = service_name
        cls._sub_service_name = sub_service_name
        cls._conn_address = f"{server_address}:50051"

        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AuthClient, cls).__new__(cls)

                cls._instance.channel = get_secure_channel(server_address)
                # cls._instance.channel = grpc.insecure_channel(cls._conn_address)

                cls._instance.stub = auth_pb2_grpc.AuthServiceStub(cls._instance.channel)

        return cls._instance

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.channel.close()

    def close(self):
        self.channel.close()

    @try_except
    def get_user_data(self, **kwargs) -> dict:
        if user_id := kwargs.get("id"):
            if user_data := cache.get(f"user_id_{user_id}"):
                return user_data

        request = auth_pb2.UserQuery(service_name=self.service_name, sub_services__name=AuthClient._sub_service_name, **kwargs)
        result = self.stub.GetUserData(request)
        dict_result = MessageToDict(result, preserving_proto_field_name=True)
        # if dict_result:
        cache_key = f"user_id_{dict_result['id']}"
        if cache_key:
            cache.set(cache_key, dict_result)
        return dict_result

        # self.get_user_data(**kwargs)

    @try_except
    def filter_user(self, **kwargs) -> dict[str, list[str]]:
        request = auth_pb2.UserQuery(service_name=self.service_name, sub_services__name=AuthClient._sub_service_name, **kwargs)
        result = self.stub.FilterUser(request)
        return MessageToDict(result, preserving_proto_field_name=True)

    @try_except
    def verify_login(self, token: str) -> dict:
        request = auth_pb2.VerifyLoginRequest(service_name=self.service_name, sub_service_name=AuthClient._sub_service_name, token=token)
        result = self.stub.VerifyLogin(request)
        return MessageToDict(result, preserving_proto_field_name=True)

    @property
    def service_name(self):
        return self._service_name

    @property
    def sub_service_name(self):
        return self._sub_service_name


import atexit

client = AuthClient()

@atexit.register
def cleanup():
    client.close()
