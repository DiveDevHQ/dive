from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
        if response.data.get('error', None):
            _response = {'status_code': response.status_code, 'error': {}}
            if response.data.get('error', None):
                _response['error']['id'] = response.data.get('error')
            if response.data.get('error_description', None):
                _response['error']['message'] = response.data.get('error_description')
            response.data = _response
        elif response.data.get('detail', None):
            response.data['error'] = {}
            response.data['error']['id'] = response.data.get('detail').code
            response.data['error']['message'] = response.data.get('detail')
            del response.data['detail']

    return response
