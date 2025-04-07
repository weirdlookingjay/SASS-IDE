from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings

class DebugJWTAuthentication(BaseJWTAuthentication):
    def get_header(self, request):
        print('\n=== JWT Authentication Debug ===\n')
        print('Headers:', dict(request.headers))
        
        auth_header = 'Authorization'
        print('\nLooking for header:', auth_header)
        
        header = request.headers.get(auth_header)
        if not header:
            print('Header not found in request.headers')
            header = request.META.get(f'HTTP_{auth_header.upper()}')
            if not header:
                print('Header not found in request.META')
                return None
        
        print('Found header:', header)
        return header.encode()

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            print('No Auth header found')
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            print('No raw token found')
            return None

        print('\nRaw token:', raw_token)
        print('\nSecret key:', settings.SECRET_KEY)
        
        try:
            validated_token = self.get_validated_token(raw_token)
            print('\nValidated token:', validated_token)
            user = self.get_user(validated_token)
            print('\nAuthenticated user:', user)
            return (user, validated_token)
        except TokenError as e:
            print('\nToken validation error:', str(e))
            raise InvalidToken(str(e))
        except Exception as e:
            print('\nAuthentication error:', str(e))
            raise
