from rest_framework.exceptions import APIException
from rest_framework import status


class BadRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'Bad Request'

class UnauthorizedException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = 'Unauthorized'
