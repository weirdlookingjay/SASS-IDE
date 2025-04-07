from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import HttpResponse
from rest_framework.response import Response

class CorsTokenObtainPairView(TokenObtainPairView):
    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response.status_code = 200
        
        # Add CORS headers
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'accept, content-type, authorization'
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Max-Age'] = '86400'
        return response

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Add CORS headers to the actual response
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
        return response

class CorsTokenRefreshView(TokenRefreshView):
    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response.status_code = 200
        
        # Add CORS headers
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'accept, content-type, authorization'
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Max-Age'] = '86400'
        return response

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Add CORS headers to the actual response
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
        return response
