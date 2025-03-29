from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, GitTemplateViewSet, ResourceClassViewSet

router = DefaultRouter()
router.register(r'templates', GitTemplateViewSet, basename='git-template')
router.register(r'resources', ResourceClassViewSet, basename='resource-class')
router.register(r'', WorkspaceViewSet, basename='workspace')

urlpatterns = [
    path('', include(router.urls)),
]
