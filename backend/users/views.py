from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, AdminUserSerializer, UserUpdateSerializer
from workspaces.permissions import IsAdminUser as CustomIsAdminUser

User = get_user_model()

class UserViewSet(ModelViewSet):
    """
    ViewSet for user management.
    - POST / is public (registration)
    - Regular users can only view and update their own profile
    - Admin users can manage all users
    """
    queryset = User.objects.all()
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':  # Registration is public
            permission_classes = [AllowAny]
        elif self.action in ['list', 'destroy', 'toggle_admin']:
            permission_classes = [IsAuthenticated, CustomIsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Use different serializers for admin/non-admin users
        """
        # For registration (create) or anonymous users, use regular serializer
        if self.action == 'create' or not self.request.user.is_authenticated:
            return UserSerializer
            
        # For authenticated users, check admin status
        if self.request.user.is_admin:
            return AdminUserSerializer
        return UserSerializer

    def get_queryset(self):
        """
        Admin users can see all users.
        Regular users can only see their own profile.
        """
        # For registration or anonymous users, return empty queryset
        if not self.request.user.is_authenticated:
            return User.objects.none()
            
        if self.request.user.is_admin:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        Get or update the current user's profile
        """
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def toggle_admin(self, request, pk=None):
        """
        Toggle admin status of a user.
        Only available to admin users.
        """
        if not request.user.is_admin:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        user.is_admin = not user.is_admin
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
