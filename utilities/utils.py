from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


class ResponseInfo:
    """
    Standard format for API responses.
    """
    def __init__(self):
        self.response = {
            "data": None,
            "error": None,
            "message": [],
            "status_code": status.HTTP_200_OK,
        }


def custom_exception_handler(exc, context):
    """
    Custom exception handler to provide consistent error response structure.
    """
    response = exception_handler(exc, context)

    if response is not None:
        response_format = ResponseInfo().response
        response_format["error"] = str(exc)
        response_format["status_code"] = response.status_code

        if response.status_code == status.HTTP_400_BAD_REQUEST:
            response_format["message"] = ["Bad request"]
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            response_format["message"] = ["Unauthorized"]
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            response_format["message"] = ["Forbidden"]
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            response_format["message"] = ["Not found"]
        else:
            response_format["message"] = ["An error occurred"]

        return Response(response_format, status=response.status_code)

    return response


def handle_success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """
    Helper function to return a standardized success response.
    """
    response_format = ResponseInfo().response
    response_format["data"] = data
    response_format["message"] = [message]
    response_format["status_code"] = status_code

    return Response(response_format, status=status_code)


def handle_error_response(error_message, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Helper function to return a standardized error response.
    """
    response_format = ResponseInfo().response
    response_format["error"] = error_message
    response_format["message"] = ["An error occurred"]
    response_format["status_code"] = status_code

    return Response(response_format, status=status_code)
