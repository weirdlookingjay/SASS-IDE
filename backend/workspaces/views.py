from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import GitTemplate, ResourceClass, Workspace
from .serializers import GitTemplateSerializer, ResourceClassSerializer, WorkspaceSerializer
from .permissions import IsAdminUser
from containers.services import DockerService

class GitTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Git templates.
    - List/Retrieve: All authenticated users
    - Create/Update/Delete: Admin users only
    """
    queryset = GitTemplate.objects.all()
    serializer_class = GitTemplateSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter templates by language"""
        queryset = GitTemplate.objects.all()
        language = self.request.query_params.get('language', None)
        if language:
            queryset = queryset.filter(language=language)
        return queryset

    @action(detail=False, methods=['get'])
    def languages(self, request):
        """Get list of available programming languages"""
        return Response(dict(GitTemplate.LANGUAGE_CHOICES))

class ResourceClassViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing resource classes.
    - List/Retrieve: All authenticated users
    - Create/Update/Delete: Admin users only
    """
    queryset = ResourceClass.objects.all()
    serializer_class = ResourceClassSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class WorkspaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing workspaces.
    Regular users can only see their own workspaces.
    Admin users can see all workspaces.
    """
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]
    docker_service = DockerService()

    def get_queryset(self):
        if self.request.user.is_admin:
            return Workspace.objects.all()
        return Workspace.objects.filter(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        workspace = self.get_object()
        success = self.docker_service.start_container(workspace)
        if success:
            return Response({'status': 'workspace started'})
        return Response(
            {'status': 'failed to start workspace'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        workspace = self.get_object()
        success = self.docker_service.stop_container(workspace)
        if success:
            return Response({'status': 'workspace stopped'})
        return Response(
            {'status': 'failed to stop workspace'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        workspace = self.get_object()
        container_status = self.docker_service.get_container_status(workspace)
        return Response(container_status)

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        workspace = self.get_object()
        container_logs = self.docker_service.get_container_logs(workspace)
        return Response({'logs': container_logs})

    def perform_create(self, serializer):
        workspace = serializer.save()
        # Initialize the container when workspace is created
        success = self.docker_service.initialize_container(workspace)
        if not success:
            workspace.delete()
            raise Exception("Failed to initialize workspace container")
