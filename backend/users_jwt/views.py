from rest_framework_simplejwt.views import TokenObtainPairView
from .authentication import DebugJWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .serializers import CustomTokenObtainPairSerializer

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]  # Allow all by default
    authentication_classes = []      # No auth by default
    
    def post(self, request, *args, **kwargs):
        # Only apply JWT auth for POST
        self.permission_classes = []
        self.authentication_classes = []
        return super().post(request, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response.status_code = 200
        response['Access-Control-Allow-Origin'] = request.headers.get('Origin')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, X-Requested-With'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '3600'
        response['Access-Control-Expose-Headers'] = 'Content-Type, Authorization'
        return response

    def post(self, request, *args, **kwargs):
        print('\n=== Login Request ===\n')
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response['Access-Control-Allow-Origin'] = request.headers.get('Origin')
            access_token = response.data['access']
            print('\n=== Access Token ===\n' + access_token)
            print('\n=== Test Command ===\ncurl -X GET http://localhost:8001/api/jwt/me/ -H "Authorization: Bearer ' + access_token + '"\n')
        return response


@method_decorator(csrf_exempt, name='dispatch')
class UserMeView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [DebugJWTAuthentication]

    def get(self, request, *args, **kwargs):
        print('Headers:', request.headers)
        print('Auth:', request.auth)
        print('User:', request.user)
        
        user = request.user
        data = {
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_staff
        }
        response = Response(data)
        
        # Set CORS headers
        origin = request.headers.get('Origin', '*')
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        if origin != '*':
            response['Access-Control-Allow-Credentials'] = 'true'
        
        return response


@method_decorator(csrf_exempt, name='dispatch')
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [DebugJWTAuthentication]

    def get(self, request, username, *args, **kwargs):
        print('Headers:', request.headers)
        print('Auth:', request.auth)
        print('Authenticated user:', request.user)
        print('Requested username:', username)
        
        User = get_user_model()
        user = get_object_or_404(User, username=username)
        
        data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_admin': user.is_staff
        }
        response = Response(data)
        
        # Set CORS headers
        origin = request.headers.get('Origin', '*')
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        if origin != '*':
            response['Access-Control-Allow-Credentials'] = 'true'
        
        return response

    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response.status_code = 200
        response['Access-Control-Allow-Origin'] = request.headers.get('Origin')
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, X-Requested-With'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '3600'
        response['Access-Control-Expose-Headers'] = 'Content-Type, Authorization'
        return response
