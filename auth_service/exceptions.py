import grpc


class GRPC_Exception(Exception):
    def __init__(self, detail, status_code=None, status_detail=None):
        match status_detail:
            case "NOT_FOUND":
                self.status_code = 404
            case "UNAUTHENTICATED" | "PERMISSION_DENIED":
                self.status_code = 403
            case "OUT_OF_RANGE" | "INVALID_ARGUMENT":
                self.status_code = 400
            case _:
                self.status_code = status_code
        self.status_detail = status_detail
        self.detail = detail

    @property
    def dict(self):
        dict_items = self.__dict__.items()
        return {k: v for k, v in dict_items if v}

    def __str__(self):
        return str(self.dict)


class GRPC_Value_Exception(GRPC_Exception):
    def __init__(self, field_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_name = field_name

    @property
    def dict(self):
        details = super().dict
        details['field_name'] = self.field_name
        return details


def try_except(func):
    def wrapper(*args, **kwargs):

        try:
            result = func(*args, **kwargs)
            return result

        except grpc.RpcError as e:
            status_code = e.code().value[0]
            status_detail = e.code().name
            detail = e.details()
            raise GRPC_Exception(status_code=status_code, status_detail=status_detail, detail=detail)

        except ValueError as e:
            import re
            error_text = e.__str__()
            field_name = re.findall(r'"([^"]+)"', error_text)[0]
            raise GRPC_Value_Exception(field_name=field_name, detail=error_text)

    return wrapper
