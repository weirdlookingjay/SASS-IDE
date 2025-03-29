from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_admin)

class IsWorkspaceOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners of a workspace or admins to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users can access any workspace
        if request.user.is_admin:
            return True
        # Regular users can only access their own workspaces
        return obj.owner == request.user
