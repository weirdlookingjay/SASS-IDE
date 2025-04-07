from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
import sys

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        print('='*80, file=sys.stderr)
        print('Serializer validate called', file=sys.stderr)
        print(f'Attrs: {attrs}', file=sys.stderr)
        
        # Call parent class validate to handle JWT token creation
        data = super().validate(attrs)
        
        # Add any custom fields to the response
        data.update({
            'username': self.user.username,
            'email': self.user.email
        })
        
        print('Validation successful', file=sys.stderr)
        print('='*80, file=sys.stderr)
        
        return data
