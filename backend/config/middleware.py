import logging
logger = logging.getLogger(__name__)

from django.http import HttpResponse

class DebugMiddleware:
    """Debug middleware to log all requests and responses"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the request
        print('\n' + '='*80)
        print(f'Request: {request.method} {request.path}')
        print(f'Headers:')
        for header, value in request.headers.items():
            print(f'  {header}: {value}')

        # Get the response
        response = self.get_response(request)

        # Log the response
        print('\nResponse:')
        print(f'  Status: {response.status_code}')
        print(f'  Headers:')
        for header, value in response.headers.items():
            print(f'    {header}: {value}')
        print('='*80 + '\n')

        return response
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.debug('='*50)
        logger.debug(f'Request: {request.method} {request.path}')
        logger.debug(f'Headers: {dict(request.headers)}')
        logger.debug(f'Body: {request.body.decode() if request.body else "No body"}')
        logger.debug('='*50)

        response = self.get_response(request)

        logger.debug('='*50)
        logger.debug(f'Response Status: {response.status_code}')
        logger.debug(f'Response Headers: {dict(response.headers)}')
        try:
            body = response.content.decode()
            logger.debug(f'Response Body: {body}')
        except:
            logger.debug('Response Body: Could not decode response content')
        logger.debug('='*50)

        return response

# Using django-cors-headers package instead of custom CORS middleware
