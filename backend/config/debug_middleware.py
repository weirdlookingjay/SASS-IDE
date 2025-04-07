import logging
logger = logging.getLogger(__name__)

class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request details
        logger.debug('='*50)
        logger.debug(f'Request: {request.method} {request.path}')
        logger.debug(f'Headers: {dict(request.headers)}')
        logger.debug(f'Body: {request.body.decode() if request.body else "No body"}')
        logger.debug('='*50)

        response = self.get_response(request)

        # Log response details
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
