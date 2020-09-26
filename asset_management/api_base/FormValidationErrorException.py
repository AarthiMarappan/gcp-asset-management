class FormValidationErrorException():
    def formErrorResponseFormat(response):
        data = response.errors
        error_response = []

        for field, value in data.items():
            field_errors = {}
            field_errors['field'] = field
            if value:
                field_errors['message'] = value[0]
            error_response.append(field_errors)
 
        return error_response