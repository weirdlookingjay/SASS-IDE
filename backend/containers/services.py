import os
import docker
from typing import Dict, Optional, List
from django.conf import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DockerService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DockerService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.client = None
            self.is_available = False
            self._initialized = True

    def _ensure_connection(self):
        """Lazy initialization of Docker connection"""
        if self.client is not None:
            return

        connection_methods = [
            # Try default first (usually works on both Windows and Linux)
            lambda: docker.from_env(),
            # Try Windows named pipe
            lambda: docker.DockerClient(base_url='npipe:////./pipe/docker_engine', timeout=5),
            # Try TCP as last resort
            lambda: docker.DockerClient(base_url='tcp://localhost:2375', timeout=5),
        ]

        for i, connect in enumerate(connection_methods):
            try:
                print(f"Trying connection method {i+1}...")
                client = connect()
                print(f"Connection established, testing with ping...")
                client.ping()
                self.client = client
                self.is_available = True
                print(f"Docker connection successful using method {i+1}")
                break
            except Exception as e:
                print(f"Connection method {i+1} failed: {str(e)}")
                continue

        if not self.is_available:
            print("Warning: All Docker connection methods failed. Container management will be disabled.")

    def _ensure_workspace_volume(self, workspace_id: int) -> Optional[str]:
        """Ensure workspace volume exists and return its name"""
        if not self.is_available:
            return None

        volume_name = f"workspace-{workspace_id}"
        try:
            # Try to get existing volume
            self.client.volumes.get(volume_name)
        except docker.errors.NotFound:
            # Create if not exists
            self.client.volumes.create(
                name=volume_name,
                driver='local',
                labels={
                    'workspace_id': str(workspace_id),
                    'created_at': datetime.utcnow().isoformat()
                }
            )
        return volume_name

    def _find_free_port(self, start: int, end: int) -> Optional[int]:
        """Find a free port between start and end"""
        import socket
        for port in range(start, end):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('', port))
                sock.close()
                return port
            except OSError:
                continue
        return None

    def create_workspace_container(
        self,
        workspace_id: int,
        image: str = "codercom/code-server:latest",
        cpu_count: int = 2,
        memory_limit: str = "4g",
        workspace_dir: str = "/workspace",
    ) -> Dict:
        """Create a new workspace container with VS Code Server."""
        self._ensure_connection()
        
        if not self.is_available:
            return {
                "container_id": None,
                "name": f"workspace-{workspace_id}",
                "status": "docker_unavailable",
                "port": None
            }

        try:
            # Ensure volume exists
            volume_name = self._ensure_workspace_volume(workspace_id)
            if not volume_name:
                return {
                    "container_id": None,
                    "name": f"workspace-{workspace_id}",
                    "status": "volume_creation_failed",
                    "port": None
                }

            # Generate a secure password
            import secrets
            import string
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))

            # Create container with dynamic port mapping
            container = self.client.containers.create(
                image=image,
                name=f"workspace-{workspace_id}",
                volumes={
                    volume_name: {'bind': workspace_dir, 'mode': 'rw'}
                },
                ports={'8080/tcp': None},  # Let Docker assign a random port
                environment={
                    'PASSWORD': password,
                    'USER_UID': '1000',
                    'USER_GID': '1000'
                },
                cpu_count=cpu_count,
                mem_limit=memory_limit,
                restart_policy={"Name": "unless-stopped"},
                healthcheck={
                    "test": ["CMD", "wget", "-q", "--spider", "http://localhost:8080"],
                    "interval": 30000000000,  # 30 seconds
                    "timeout": 3000000000,    # 3 seconds
                    "retries": 3
                }
            )

            # Start the container
            container.start()
            container.reload()  # Refresh container info to get assigned port

            # Get the assigned port
            port = None
            if container.attrs['NetworkSettings']['Ports'] and '8080/tcp' in container.attrs['NetworkSettings']['Ports']:
                port_mapping = container.attrs['NetworkSettings']['Ports']['8080/tcp']
                if port_mapping:
                    port = int(port_mapping[0]['HostPort'])

            return {
                "container_id": container.id,
                "name": container.name,
                "status": container.status,
                "port": port,
                "password": password  # Return the password so it can be stored or shown to the user
            }

        except Exception as e:
            print(f"Error creating container: {str(e)}")
            return {
                "container_id": None,
                "name": f"workspace-{workspace_id}",
                "status": f"error: {str(e)}",
                "port": None
            }

    def get_container_status(self, container_id: str) -> dict:
        """Get detailed status of a container including health and resource usage."""
        try:
            container = self.client.containers.get(container_id)
            stats = container.stats(stream=False)  # Get a single stats reading
            
            # Calculate CPU usage percentage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 * len(stats['cpu_stats']['cpu_usage']['percpu_usage'])
            
            # Calculate memory usage
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100.0
            
            return {
                'status': container.status,
                'health': container.attrs['State'].get('Health', {}).get('Status', 'none'),
                'cpu_percent': round(cpu_percent, 2),
                'memory_usage_mb': round(memory_usage / (1024 * 1024), 2),
                'memory_limit_mb': round(memory_limit / (1024 * 1024), 2),
                'memory_percent': round(memory_percent, 2)
            }
        except Exception as e:
            return {
                'status': 'error',
                'health': 'none',
                'error': str(e)
            }

    def get_container_logs(self, container_id: str, tail: int = 100) -> str:
        """Get the latest logs from a container."""
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail, timestamps=True).decode('utf-8')
            return logs
        except Exception as e:
            return f"Error getting logs: {str(e)}"

    def start_container(self, container_id: str) -> bool:
        """Start a stopped container."""
        try:
            container = self.client.containers.get(container_id)
            container.start()
            return True
        except Exception as e:
            logger.error(f"Error starting container {container_id}: {str(e)}")
            return False

    def stop_container(self, container_id: str) -> bool:
        """Stop a running container."""
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=10)  # Give it 10 seconds to stop gracefully
            return True
        except Exception as e:
            logger.error(f"Error stopping container {container_id}: {str(e)}")
            return False

    def restart_container(self, container_id: str) -> bool:
        """Restart a container."""
        try:
            container = self.client.containers.get(container_id)
            container.restart(timeout=10)  # Give it 10 seconds to stop gracefully
            return True
        except Exception as e:
            logger.error(f"Error restarting container {container_id}: {str(e)}")
            return False

    def cleanup_unused_volumes(self, older_than_days: int = 7) -> List[str]:
        """Clean up unused workspace volumes older than specified days."""
        self._ensure_connection()
        
        if not self.is_available:
            return []

        cleaned_volumes = []
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            for volume in self.client.volumes.list():
                # Check if it's a workspace volume
                if not volume.name.startswith('workspace-'):
                    continue

                # Check creation date from labels
                created_at = volume.attrs['Labels'].get('created_at')
                if not created_at:
                    continue

                volume_date = datetime.fromisoformat(created_at)
                if volume_date < cutoff_date:
                    volume.remove(force=True)
                    cleaned_volumes.append(volume.name)

            return cleaned_volumes
        except Exception as e:
            print(f"Error cleaning up volumes: {str(e)}")
            return []

    def delete_container(self, container_id: str, remove_volume: bool = True) -> bool:
        """Delete a container and optionally its volume."""
        self._ensure_connection()
        
        if not self.is_available:
            return False

        try:
            container = self.client.containers.get(container_id)
            # Get volume info before removing container
            volume_name = None
            for mount in container.attrs.get('Mounts', []):
                if mount['Type'] == 'volume' and mount['Name'].startswith('workspace-'):
                    volume_name = mount['Name']
                    break

            # Remove container
            container.remove(force=True)

            # Remove volume if requested
            if remove_volume and volume_name:
                try:
                    volume = self.client.volumes.get(volume_name)
                    volume.remove(force=True)
                except Exception as e:
                    print(f"Error removing volume {volume_name}: {str(e)}")

            return True
        except Exception as e:
            print(f"Error deleting container: {str(e)}")
            return False

    def get_container_status(self, container_id: str) -> Optional[Dict]:
        """Get container status and information."""
        self._ensure_connection()
        
        if not self.is_available:
            return {
                "status": "docker_unavailable",
                "is_running": False
            }

        try:
            container = self.client.containers.get(container_id)
            container.reload()
            
            # Get volume info
            volume_info = None
            for mount in container.attrs.get('Mounts', []):
                if mount['Type'] == 'volume' and mount['Name'].startswith('workspace-'):
                    volume_info = {
                        'name': mount['Name'],
                        'path': mount['Destination']
                    }
                    break

            return {
                "id": container.id,
                "status": container.status,
                "name": container.name,
                "ports": container.ports,
                "created": container.attrs["Created"],
                "state": container.attrs["State"],
                "volume": volume_info,
                "resource_usage": {
                    "cpu_percent": container.stats(stream=False).get('cpu_stats', {}).get('cpu_usage', {}).get('total_usage', 0),
                    "memory_usage": container.stats(stream=False).get('memory_stats', {}).get('usage', 0),
                }
            }
        except Exception as e:
            print(f"Error getting container status: {str(e)}")
            return None
