from api_base.response import Response
from rest_framework import status

class PostResponse(Response):
    def __init__(self, data = None, errors = None, status = status.HTTP_201_CREATED):
        super(PostResponse, self).__init__(data, errors, status)
