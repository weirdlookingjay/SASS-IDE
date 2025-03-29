from datetime import datetime
from django.utils import timezone
from .services import DockerService
from workspaces.models import Workspace

class ContainerManager:
    def __init__(self):
        self.docker_service = DockerService()

    def create_workspace_container(self, workspace: Workspace) -> bool:
        """Create and start a new container for a workspace."""
        try:
            # Get resource specifications from the resource class
            cpu_count = workspace.resource_class.cpu_count
            memory_gb = workspace.resource_class.ram_gb
            
            # Create container
            container_info = self.docker_service.create_workspace_container(
                workspace_id=workspace.id,
                cpu_count=cpu_count,
                memory_limit=f"{memory_gb}g"
            )

            # Update workspace with container information
            workspace.container_id = container_info["container_id"]
            workspace.container_status = container_info["status"]
            workspace.container_port = container_info["port"]
            workspace.is_running = True
            workspace.last_accessed = timezone.now()
            workspace.save()

            return True
        except Exception as e:
            print(f"Error creating container for workspace {workspace.id}: {str(e)}")
            return False

    def stop_workspace_container(self, workspace: Workspace) -> bool:
        """Stop a workspace container."""
        if not workspace.container_id:
            return False

        if self.docker_service.stop_container(workspace.container_id):
            workspace.is_running = False
            workspace.container_status = "stopped"
            workspace.save()
            return True
        return False

    def start_workspace_container(self, workspace: Workspace) -> bool:
        """Start a workspace container."""
        if not workspace.container_id:
            return False

        if self.docker_service.start_container(workspace.container_id):
            workspace.is_running = True
            workspace.container_status = "running"
            workspace.last_accessed = timezone.now()
            workspace.save()
            return True
        return False

    def delete_workspace_container(self, workspace: Workspace) -> bool:
        """Delete a workspace container."""
        if not workspace.container_id:
            return True

        if self.docker_service.delete_container(workspace.container_id):
            workspace.container_id = None
            workspace.container_status = None
            workspace.container_port = None
            workspace.is_running = False
            workspace.save()
            return True
        return False

    def get_workspace_status(self, workspace: Workspace) -> dict:
        """Get the current status of a workspace container."""
        if not workspace.container_id:
            return {
                "status": "not_created",
                "is_running": False
            }

        container_status = self.docker_service.get_container_status(workspace.container_id)
        if not container_status:
            return {
                "status": "not_found",
                "is_running": False
            }

        return {
            "status": container_status["status"],
            "is_running": container_status["status"] == "running",
            "ports": container_status["ports"],
            "state": container_status["state"]
        }
