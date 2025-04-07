from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .serializers import UserSerializer
from django.contrib.auth import authenticate, get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError({
                'error': 'Both username and password are required.',
                'detail': 'Please provide both username and password.'
            })

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'error': 'Invalid credentials',
                'detail': f'No account found with username: {username}'
            })

        if not user.is_active:
            raise serializers.ValidationError({
                'error': 'Account disabled',
                'detail': 'This account has been deactivated.'
            })

        if not user.check_password(password):
            raise serializers.ValidationError({
                'error': 'Invalid credentials',
                'detail': 'The password you entered is incorrect.'
            })

        refresh = self.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }
        return data
            
        self.user = user
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        logger.debug(f'Validation successful for user: {username}')
        return data
