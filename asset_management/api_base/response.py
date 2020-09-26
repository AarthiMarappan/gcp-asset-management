from django.http.response import JsonResponse

class Response():
    def __init__(self, data, errors, statusCode):
        self.data = data
        self.errors = errors
        self.status = statusCode

    def formatResponse(self):
        response_data = {
            'data': self.data,
            'errors': self.errors
        }
        return JsonResponse(response_data, status = self.status)
