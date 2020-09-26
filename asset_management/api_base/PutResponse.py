from api_base.response import Response
from rest_framework import status

class PutResponse(Response):
    def __init__(self, data = None, errors = None, status = status.HTTP_200_OK):
        super(PutResponse, self).__init__(data, errors, status)
