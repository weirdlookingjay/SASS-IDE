import os
import docker
import logging
import secrets
import subprocess
import tempfile
import time
import platform
from pathlib import Path
from django.conf import settings
from docker.errors import DockerException
import shutil
import tarfile
from io import BytesIO

logger = logging.getLogger(__name__)

class DockerService:
    def __init__(self, workspace_root):
        """Initialize Docker service"""
        self.workspace_root = workspace_root
        self.is_available = False
        self.client = None
        self._initialize_docker_client()

    def _initialize_docker_client(self):
        """Initialize Docker client based on platform"""
        try:
            if os.name == 'nt':
                # Windows - explicitly use named pipe
                self.client = docker.DockerClient(
                    base_url='npipe:////./pipe/docker_engine',
                    timeout=120
                )
                self.client.ping()  # Test connection
                self.is_available = True
                logger.info("Connected to Docker daemon via Windows named pipe")
            else:
                # Unix-like systems - use default socket
                self.client = docker.from_env(timeout=120)
                self.client.ping()
                self.is_available = True
                logger.info("Connected to Docker daemon via Unix socket")
        except Exception as e:
            error_msg = str(e)
            if os.name == 'nt':
                error_msg = "Error connecting to Docker. Please ensure Docker Desktop is running and WSL integration is disabled."
            raise DockerException(f"Error initializing Docker client: {error_msg}")

    def _find_free_port(self, start=8000, end=9000):
        """Find a free port in the given range"""
        import socket
        for port in range(start, end):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('', port))
                    return port
                except OSError:
                    continue
        raise RuntimeError(f"No free ports found in range {start}-{end}")

    def create_workspace_container(self, workspace_id, cpu_count=2, memory_limit="4g", workspace_dir="/workspace", image="codercom/code-server:latest"):
        """Create a new container for a workspace"""
        try:
            # Generate container name and password
            container_name = f"workspace_{workspace_id}"
            password = secrets.token_urlsafe(16)

            # Check if container already exists
            try:
                existing_container = self.client.containers.get(container_name)
                logger.info(f"Found existing container {container_name}")
                
                # Remove existing container if it exists
                existing_container.remove(force=True)
                logger.info(f"Removed existing container {container_name}")
            except docker.errors.NotFound:
                pass

            # Find a free port
            port = self._find_free_port()

            # Resource limits
            cpu_period = 100000
            cpu_quota = int(cpu_count * cpu_period)

            # Create container
            container = self.client.containers.run(
                image=image,
                name=container_name,
                detach=True,
                environment={
                    "PASSWORD": password,
                    "WORKSPACE_ID": str(workspace_id)
                },
                volumes={
                    self.workspace_root: {
                        'bind': workspace_dir,
                        'mode': 'rw'
                    }
                },
                ports={'8080/tcp': port},  # Map container's 8080 to host's free port
                cpu_period=cpu_period,
                cpu_quota=cpu_quota,
                mem_limit=memory_limit,
                restart_policy={
                    'Name': 'unless-stopped'
                }
            )

            logger.info(f"Created container {container_name} with ID {container.id} on port {port}")

            # Construct container URL
            container_url = f'http://localhost:{port}?password={password}'

            # Return container info
            return {
                'container_id': container.id,
                'name': container_name,
                'password': password,
                'port': port,
                'container_url': container_url,
                'status': 'created'
            }

        except Exception as e:
            error_msg = f"Failed to create workspace container: {str(e)}"
            logger.error(error_msg)
            return {'error': error_msg, 'status': 'failed'}

    def _check_docker_daemon(self):
        """Check if Docker daemon is running"""
        try:
            if not self.client:
                self._initialize_docker_client()
            self.client.ping()
            return True
        except Exception as e:
            error_msg = str(e)
            if os.name == 'nt':
                error_msg = "Docker is not running. Please ensure Docker Desktop is running."
            raise DockerException(f"Error checking Docker daemon: {error_msg}")

    def _get_host_path(self, path):
        """Get the appropriate host path based on platform"""
        if os.name == 'nt':
            # On Windows, use the path as is
            return os.path.abspath(path)
        else:
            # On Unix-like systems, return path as is
            return path

    def _handle_docker_error(self):
        """Handle Docker initialization errors"""
        try:
            if platform.system() == 'Windows':
                # Check if Docker Desktop is running
                subprocess.run(['powershell.exe', 'Get-Process', 'com.docker.backend'], 
                            check=True, capture_output=True)
                logger.error("Docker Desktop is running but WSL integration might be disabled")
            else:
                logger.error("Docker daemon is not running or not accessible")
        except subprocess.CalledProcessError:
            logger.error("Docker Desktop is not running")
        except Exception as e:
            logger.error(f"Error checking Docker status: {e}")

    def _get_image_for_workspace(self, workspace):
        """Get the appropriate container image based on language"""
        if not workspace.git_template:
            return 'codercom/code-server:latest'

        base_image = 'codercom/code-server:latest'
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        language = workspace.git_template.language.lower()
        logger.info(f"Creating workspace for language: {language}")
        
        if language == 'go':
            # Check if image already exists
            try:
                existing_image = self.client.images.get(f"ide-{language}:latest")
                logger.info(f"Found existing image: {existing_image.tags}")
                return f"ide-{language}:latest"
            except Exception as e:
                logger.info(f"No existing image found, building new one: {str(e)}")

            setup_commands = [
                'set -ex',  # Make script verbose
                'apt-get update',
                'apt-get install -y --no-install-recommends wget ca-certificates git curl',
                'wget -q https://golang.org/dl/go1.21.0.linux-amd64.tar.gz',
                'rm -rf /usr/local/go && tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz',
                'rm go1.21.0.linux-amd64.tar.gz',
                'mkdir -p /home/coder/go/{bin,pkg,src}',
                'chown -R coder:coder /home/coder/go'
            ]

            dockerfile_content = f"""
FROM {base_image}

USER root

# Set environment variables first
ENV PATH=/usr/local/go/bin:/home/coder/go/bin:/home/coder/.local/bin:/home/coder/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV GOROOT=/usr/local/go
ENV GOPATH=/home/coder/go
ENV GOBIN=/home/coder/go/bin

# Run setup commands
RUN {' && '.join(setup_commands)}

# Add environment variables to profile and bashrc
RUN echo 'export PATH=/usr/local/go/bin:/home/coder/go/bin:$PATH' >> /etc/profile && \\
    echo 'export GOROOT=/usr/local/go' >> /etc/profile && \\
    echo 'export GOPATH=/home/coder/go' >> /etc/profile && \\
    echo 'export GOBIN=/home/coder/go/bin' >> /etc/profile && \\
    echo 'export PATH=/usr/local/go/bin:/home/coder/go/bin:$PATH' >> /home/coder/.bashrc && \\
    echo 'export GOROOT=/usr/local/go' >> /home/coder/.bashrc && \\
    echo 'export GOPATH=/home/coder/go' >> /home/coder/.bashrc && \\
    echo 'export GOBIN=/home/coder/go/bin' >> /home/coder/.bashrc && \\
    chown -R coder:coder /home/coder/.bashrc

USER coder

# Final verification
RUN bash -c 'source /etc/profile && source ~/.bashrc && \\
    echo "=== Final Verification ===" && \\
    echo "PATH=$PATH" && \\
    echo "GOROOT=$GOROOT" && \\
    echo "GOPATH=$GOPATH" && \\
    ls -la /usr/local/go/bin && \\
    which go && \\
    go version'
"""
            logger.info("Writing Dockerfile...")
            dockerfile_path = os.path.join(temp_dir, 'Dockerfile')
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)

            # Build custom image
            tag = f"ide-{language}:latest"
            try:
                logger.info(f"Building custom image for {language}")
                logger.info(f"Dockerfile contents:\n{dockerfile_content}")
                
                # Build the image with verbose output
                logger.info("Starting Docker build...")
                response = self.client.api.build(
                    path=temp_dir,
                    tag=tag,
                    rm=True,
                    forcerm=True
                )
                
                # Log all build output
                for chunk in response:
                    if isinstance(chunk, dict):
                        if 'stream' in chunk:
                            log_line = chunk['stream'].strip()
                            if log_line:
                                logger.info(f"Build: {log_line}")
                        elif 'error' in chunk:
                            error_msg = chunk['error']
                            logger.error(f"Build error: {error_msg}")
                            raise Exception(f"Docker build failed: {error_msg}")
                
                # Verify image was built
                built_image = self.client.images.get(tag)
                logger.info(f"Successfully built image: {built_image.tags}")
                return tag
            except Exception as e:
                logger.error(f"Failed to build custom image: {str(e)}")
                raise  # Re-raise the exception instead of silently falling back
        else:
            return base_image

    def _initialize_container(self, container, workspace):
        """Initialize a container with template files"""
        try:
            logger.info(f"Initializing container for workspace {workspace.id}")
            
            # No need to clone template - files are already in workspace directory
            workspace_path = os.path.join(settings.WORKSPACE_ROOT, str(workspace.id))
            if not os.path.exists(workspace_path):
                logger.error(f"Workspace directory does not exist: {workspace_path}")
                return False

            # Copy files from workspace directory to container
            logger.info(f"Copying files from {workspace_path} to container")
            tar_stream = BytesIO()
            with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                for root, dirs, files in os.walk(workspace_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, workspace_path)
                        tar.add(file_path, arcname=arcname)

            tar_stream.seek(0)
            if not container.put_archive('/home/coder/project', tar_stream.read()):
                logger.error("Failed to copy files to container")
                return False

            logger.info(f"Container {container.id} initialized successfully for workspace {workspace.id}")
            return True

        except Exception as e:
            logger.error(f"Error initializing container: {str(e)}")
            return False

    def initialize_container(self, workspace):
        """Initialize a new container for a workspace"""
        try:
            workspace_path = os.path.join(settings.WORKSPACE_ROOT, str(workspace.id))
            
            # Don't clean up workspace directory - Git service already put files there
            # if os.path.exists(workspace_path):
            #     logger.info(f"Cleaning up existing workspace directory: {workspace_path}")
            #     shutil.rmtree(workspace_path)
            
            logger.info(f"Creating workspace for language: {workspace.git_template.language}")

            # Get image for workspace
            image = self._get_image_for_workspace(workspace)
            if not image:
                raise Exception("No suitable image found for workspace")
            logger.info(f"Using image: {image} for workspace {workspace.id}")

            # Create container
            logger.info(f"Creating container for workspace {workspace.id}")
            container = self._create_container(workspace, image)
            if not container:
                raise Exception("Failed to create container")
            
            container_id = container.id
            logger.info(f"Container {container_id} created successfully")

            # Initialize container with template files
            if not self._initialize_container(container, workspace):
                self._cleanup_failed_workspace(workspace, container_id)  # Don't pass workspace_path
                raise Exception("Failed to initialize container")

            # Update workspace with container info
            workspace.container_id = container.id
            workspace.container_status = 'created'
            workspace.container_port = self._get_container_port(container)
            workspace.container_url = self._get_container_url(workspace)
            workspace.save()

            logger.info(f"Container {container_id} initialized successfully for workspace {workspace.id}")
            return True

        except Exception as e:
            logger.error(f"Error initializing container: {str(e)}")
            return False

    def start_container(self, workspace):
        """Start a container for a workspace"""
        try:
            if workspace.container_id:
                # Try to get existing container
                try:
                    container = self.client.containers.get(workspace.container_id)
                    if container.status != 'running':
                        container.start()
                    return True
                except docker.errors.NotFound:
                    # Container doesn't exist anymore, create new one
                    pass

            # Create and start new container
            container = self.create_container(workspace)
            if container:
                workspace.container_id = container.id
                workspace.container_status = 'running'
                workspace.container_url = f"http://localhost:{workspace.container_port}"
                workspace.save()
                return True

            return False

        except DockerException as e:
            logger.error(f"Docker error starting container: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error starting container: {str(e)}")
            return False

    def stop_container(self, workspace):
        """Stop a container for a workspace"""
        try:
            if workspace.container_id:
                try:
                    container = self.client.containers.get(workspace.container_id)
                    container.stop()
                    workspace.container_status = 'stopped'
                    workspace.save()
                    return True
                except docker.errors.NotFound:
                    # Container already gone
                    pass
            return True

        except DockerException as e:
            logger.error(f"Docker error stopping container: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error stopping container: {str(e)}")
            return False

    def create_container(self, workspace):
        """Create a new container for a workspace"""
        try:
            workspace_path = os.path.join(settings.WORKSPACE_ROOT, str(workspace.id))
            container_name = f"workspace_{workspace.id}"

            # Get next available port starting from base port
            base_port = 8000
            used_ports = set(
                int(c.ports.get('8080/tcp', [{'HostPort': '0'}])[0]['HostPort'])
                for c in self.client.containers.list(all=True)
                if c.ports and '8080/tcp' in c.ports
            )
            port = base_port
            while port in used_ports:
                port += 1

            # Save the port to workspace
            workspace.container_port = port
            workspace.save()

            # Create container
            container = self._create_container(workspace, self._get_image_for_workspace(workspace))
            if not container:
                raise Exception("Failed to create container")
            
            return container

        except DockerException as e:
            logger.error(f"Docker error creating container: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error creating container: {str(e)}")
            return None

    def delete_container(self, workspace):
        """Delete a container for a workspace"""
        try:
            if workspace.container_id:
                try:
                    container = self.client.containers.get(workspace.container_id)
                    container.stop()
                    container.remove()
                except docker.errors.NotFound:
                    # Container already gone
                    pass
            return True

        except DockerException as e:
            logger.error(f"Docker error deleting container: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error deleting container: {str(e)}")
            return False

    def get_container_status(self, workspace):
        """Get the current status of a container"""
        try:
            if not workspace.container_id:
                return False

            try:
                container = self.client.containers.get(workspace.container_id)
                return container.status == 'running'
            except docker.errors.NotFound:
                # Container doesn't exist, update workspace status
                self._update_workspace_status(workspace, False)
                return False

        except Exception as e:
            logger.error(f"Error checking container status for workspace {workspace.id}: {str(e)}")
            return False

    def restart_container(self, workspace):
        """Restart a workspace container"""
        self.stop_container(workspace)
        return self.initialize_container(workspace)

    def _update_workspace_status(self, workspace, is_running):
        """Update workspace status and clear container info if stopped"""
        workspace.is_running = is_running
        if not is_running:
            workspace.container_id = None
            workspace.container_url = None
            workspace.container_port = None
            workspace.container_status = 'stopped'
            workspace.container_password = None
        workspace.save()

    def _cleanup_failed_workspace(self, workspace, container_id=None):
        """Clean up resources after a failed workspace initialization"""
        try:
            # Stop and remove container if it exists
            if container_id:
                try:
                    container = self.client.containers.get(container_id)
                    container.stop()
                    container.remove()
                    logger.info(f"Cleaned up container {container_id}")
                except docker.errors.NotFound:
                    logger.info(f"Container {container_id} already removed")
                except Exception as e:
                    logger.error(f"Error cleaning up container: {str(e)}")

            # Update workspace status
            try:
                workspace.container_id = None
                workspace.container_status = 'failed'
                workspace.container_port = None
                workspace.container_url = None
                workspace.container_password = None
                workspace.is_running = False
                workspace.save()
                logger.info(f"Updated workspace {workspace.id} status to failed")
            except Exception as e:
                logger.error(f"Error updating workspace status: {str(e)}")

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            # Don't re-raise the exception since this is cleanup code

    def _create_container(self, workspace, image):
        """Create a new container for a workspace"""
        try:
            container_name = f"workspace_{workspace.id}"

            # Use existing password if available, otherwise generate new one
            password = workspace.container_password or self._generate_password()
            workspace.container_password = password  # Save password for later use
            workspace.save()

            # Get user's SSH directory path and ensure it exists
            ssh_dir = os.path.expanduser('~/.ssh')
            if not os.path.exists(ssh_dir):
                raise Exception("SSH directory not found. Please ensure SSH keys are set up.")

            # Calculate port based on workspace ID to ensure consistency
            container_port = 8000 + workspace.id
            workspace_path = os.path.join(settings.WORKSPACE_ROOT, str(workspace.id))

            # Create container config with appropriate paths
            container_config = {
                'name': container_name,
                'image': image,
                'volumes': {
                    workspace_path: {
                        'bind': '/home/coder/project',
                        'mode': 'rw'
                    },
                    ssh_dir: {
                        'bind': '/home/coder/.ssh',
                        'mode': 'ro'
                    }
                },
                'working_dir': '/home/coder/project',
                'environment': {
                    'WORKSPACE_ID': str(workspace.id),
                    'PASSWORD': password,  # Use the same password
                    'DEFAULT_WORKSPACE': '/home/coder/project',
                    'PATH': '/usr/local/go/bin:/home/coder/go/bin:/home/coder/.local/bin:/home/coder/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                    'GIT_SSH_COMMAND': 'ssh -o StrictHostKeyChecking=no',
                    'GOROOT': '/usr/local/go',
                    'GOPATH': '/home/coder/go',
                    'GOBIN': '/home/coder/go/bin',
                    'SHELL': '/bin/bash',
                    'DOCKER_USER': workspace.owner,  # Pass owner username to container
                    'DJANGO_SESSION_COOKIE_NAME': 'sessionid',  # Match Django session cookie
                    'DJANGO_SESSION_COOKIE_DOMAIN': 'localhost',  # Match Django cookie domain
                    'DJANGO_SESSION_COOKIE_PATH': '/',  # Match Django cookie path
                    'DJANGO_SESSION_COOKIE_SAMESITE': 'None',  # Allow cross-origin
                    'DJANGO_SESSION_COOKIE_SECURE': 'false',  # Match Django setting
                    'DJANGO_SECRET_KEY': settings.SECRET_KEY,  # Share Django secret key
                },
                'cpu_count': workspace.resource_class.cpu_count,
                'mem_limit': f"{workspace.resource_class.ram_gb}g",
                'detach': True,
                'tty': True,
                'ports': {
                    '8080/tcp': container_port,  # Map container's 8080 to host's dynamic port
                }
            }

            # Create and start the container
            container = self.client.containers.run(**container_config)
            workspace.container_port = container_port  # Save the mapped port
            workspace.save()
            return container

        except docker.errors.APIError as e:
            logger.error(f"Docker API error creating container: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error creating container: {str(e)}")
            return None

    def _get_container_port(self, container):
        """Get the port for a container"""
        try:
            ports = container.ports.get('8080/tcp')
            if ports:
                return int(ports[0]['HostPort'])
            return None
        except Exception as e:
            logger.error(f"Error getting container port: {str(e)}")
            return None

    def _get_container_url(self, workspace):
        """Get the URL for a workspace"""
        # Use the mapped port from the container config
        return f"http://localhost:{workspace.container_port}"

    def _generate_password(self):
        """Generate a random password for the container"""
        return secrets.token_urlsafe(32)
