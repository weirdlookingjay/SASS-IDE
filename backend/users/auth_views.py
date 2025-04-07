from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class CORSTokenObtainPairView(TokenObtainPairView):
    def dispatch(self, request, *args, **kwargs):
        print('\n=== Token View Received Request ===')        
        print(f'Method: {request.method}')
        print(f'Headers: {dict(request.headers)}\n')
        response = super().dispatch(request, *args, **kwargs)
        print('\n=== Sending Response ===')        
        print(f'Status: {response.status_code}')
        print(f'Headers: {dict(response.headers)}\n')
        return response

    def options(self, request, *args, **kwargs):
        print('\n=== Handling OPTIONS request ===')
        response = Response()
        origin = request.headers.get('Origin', 'http://localhost:3000')
        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Accept, Content-Type, Authorization, X-Requested-With"
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Max-Age"] = "86400"
        print(f'Response Headers: {dict(response.headers)}\n')
        return response

    def post(self, request, *args, **kwargs):
        print('\n=== Handling POST request ===')
        response = super().post(request, *args, **kwargs)
        origin = request.headers.get('Origin', 'http://localhost:3000')
        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Credentials"] = "true"
        print(f'Response Headers: {dict(response.headers)}\n')
        return response
