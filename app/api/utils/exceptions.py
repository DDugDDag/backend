# app/api/utils/exceptions.py
class APIException(Exception):
    def __init__(self, message: str, status_code: int | None = None, api_name: str = ""):
        self.message = message
        self.status_code = status_code
        self.api_name = api_name
        super().__init__(self.message)

class NetworkException(APIException):
    pass

class AuthenticationException(APIException):
    pass

class DataFormatException(APIException):
    pass
