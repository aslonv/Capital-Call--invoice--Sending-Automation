# api/exceptions.py

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        print(f"Unhandled exception: {exc}")
        return Response({
            "error": "An unexpected error occurred."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response