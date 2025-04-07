import logging
import json

logger = logging.getLogger('cors_middleware')
logger.setLevel(logging.DEBUG)

# Create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class CORSMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def custom_start_response(status, headers, exc_info=None):
            # Get the request method and origin
            method = environ.get('REQUEST_METHOD')
            origin = environ.get('HTTP_ORIGIN', '')
            path = environ.get('PATH_INFO', '')
            
            logger.debug(f'Request: {method} {path}')
            logger.debug(f'Origin: {origin}')
            logger.debug(f'Headers received: {json.dumps(dict(environ), default=str)}')

            if origin == 'http://localhost:3000':
                logger.debug('Origin matched - adding CORS headers')
                # Add CORS headers to the response
                cors_headers = [
                    ('Access-Control-Allow-Origin', origin),
                    ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
                    ('Access-Control-Allow-Headers', 'Authorization, Content-Type, X-Requested-With'),
                    ('Access-Control-Allow-Credentials', 'true'),
                    ('Access-Control-Max-Age', '3600'),
                ]
                
                # Add CORS headers to the existing headers
                new_headers = []
                for key, value in headers:
                    if key.lower() not in [h[0].lower() for h in cors_headers]:
                        new_headers.append((key, value))
                headers = new_headers + cors_headers

                logger.debug(f'Final headers: {headers}')

                # Handle preflight requests
                if method == 'OPTIONS':
                    logger.debug('Handling OPTIONS request - returning 200')
                    return start_response('200 OK', headers)
            else:
                logger.debug('Origin did not match http://localhost:3000 - no CORS headers added')

            logger.debug(f'Returning response with status {status}')
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)
