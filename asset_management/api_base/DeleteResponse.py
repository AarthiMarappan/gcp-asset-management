from api_base.response import Response
from rest_framework import status

class DeleteResponse(Response):
    def __init__(self, data = None, errors = None, status = status.HTTP_204_NO_CONTENT):
        super(DeleteResponse, self).__init__(data, errors, status)
