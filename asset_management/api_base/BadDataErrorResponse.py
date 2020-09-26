from api_base.response import Response
from rest_framework import status

class BadDataErrorResponse(Response):
    def __init__(self, data = None, errors = None, status = status.HTTP_400_BAD_REQUEST):
        super(BadDataErrorResponse, self).__init__(data, errors, status)
