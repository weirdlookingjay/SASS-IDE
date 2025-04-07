from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import ValidationError
from .serializers_jwt import CustomTokenObtainPairSerializer
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
import logging
import sys

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        print('='*50, file=sys.stderr)
        print('CUSTOM TOKEN VIEW CALLED', file=sys.stderr)
        print(f'Request data: {request.data}', file=sys.stderr)
        
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Try direct authentication first
        user = authenticate(username=username, password=password)
        print(f'Direct auth result: {user}', file=sys.stderr)
        
        if not user:
            return Response({
                'error': 'Invalid credentials',
                'detail': 'Username or password is incorrect'
            }, status=401)
            
        # If we get here, authentication succeeded
        try:
            response = super().post(request, *args, **kwargs)
            print('JWT token generated successfully', file=sys.stderr)
            print('='*50, file=sys.stderr)
            return response
            
        except Exception as e:
            print(f'Error generating token: {str(e)}', file=sys.stderr)
            print('='*50, file=sys.stderr)
            return Response({
                'error': 'Authentication failed',
                'detail': str(e)
            }, status=401)
