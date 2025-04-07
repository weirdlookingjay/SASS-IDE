import os
import shutil
import stat
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def handle_remove_readonly(func, path, exc):
    """Error handler for shutil.rmtree to handle readonly files"""
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
        # Change file permissions
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        # Retry the operation
        func(path)
    else:
        raise

class GitService:
    def __init__(self):
        self.workspace_root = settings.WORKSPACE_ROOT

    def _set_directory_permissions(self, path):
        """Recursively set permissions on a directory"""
        try:
            # Set directory permissions
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            
            # Recursively set permissions on all files and subdirectories
            for root, dirs, files in os.walk(path):
                for d in dirs:
                    try:
                        os.chmod(os.path.join(root, d), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    except Exception as e:
                        logger.warning(f"Failed to change directory permissions: {str(e)}")
                
                for f in files:
                    try:
                        os.chmod(os.path.join(root, f), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    except Exception as e:
                        logger.warning(f"Failed to change file permissions: {str(e)}")
        except Exception as e:
            logger.error(f"Error setting directory permissions: {str(e)}")

    def _download_file(self, url, dest_path):
        """Download a file from GitHub"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            logger.error(f"Failed to download file {url}: {str(e)}")
            return False

    def _download_directory_contents(self, owner, repo, path, branch, workspace_path, base_path=None):
        """Recursively download directory contents from GitHub"""
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        logger.info(f"Fetching contents from: {api_url}")
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            items = response.json()

            if not isinstance(items, list):
                logger.error(f"Invalid response from GitHub API for {path}: {items}")
                return False

            logger.info(f"Found {len(items)} items in {path}")
            
            # If this is the first call (base_path is None), set it to the template path
            if base_path is None:
                base_path = path

            for item in items:
                # Calculate the relative path from the base template directory
                relative_path = item['path'].replace(base_path + '/', '')
                local_path = os.path.join(workspace_path, relative_path)
                logger.info(f"Processing {item['type']}: {item['path']} -> {local_path}")

                if item['type'] == 'file':
                    # Download file
                    logger.info(f"Downloading file: {item['download_url']} -> {local_path}")
                    if not self._download_file(item['download_url'], local_path):
                        logger.error(f"Failed to download file: {item['path']}")
                        return False
                    logger.info(f"Successfully downloaded: {local_path}")
                elif item['type'] == 'dir':
                    # Create directory and recurse
                    logger.info(f"Creating directory: {local_path}")
                    os.makedirs(local_path, exist_ok=True)
                    logger.info(f"Recursing into directory: {item['path']}")
                    if not self._download_directory_contents(owner, repo, item['path'], branch, workspace_path, base_path):
                        return False

            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get directory contents for {path}: {str(e)}")
            return False

    def clone_repository(self, workspace):
        """Clone a repository for a workspace"""
        try:
            workspace_path = os.path.join(self.workspace_root, str(workspace.id))
            
            # Skip if no template or repository URL
            if not workspace.git_template or not workspace.git_template.repository_url:
                logger.info("No template or repository URL specified")
                return True

            # Clean up any existing workspace directory
            if os.path.exists(workspace_path):
                logger.info(f"Cleaning up existing workspace directory: {workspace_path}")
                shutil.rmtree(workspace_path, onerror=handle_remove_readonly)

            # Create workspace directory
            logger.info(f"Creating workspace directory: {workspace_path}")
            os.makedirs(workspace_path, exist_ok=True)
            self._set_directory_permissions(workspace_path)

            # Parse GitHub URL
            repo_url = workspace.git_template.repository_url
            logger.info(f"Processing repository URL: {repo_url}")
            
            # Remove .git extension if present
            repo_url = repo_url.replace('.git', '')
            
            # Remove /tree/branch if present
            if '/tree/' in repo_url:
                repo_url = repo_url.split('/tree/')[0]
            
            # Split URL into parts
            parts = repo_url.rstrip('/').split('/')
            owner = parts[-2]  # Second to last part is owner
            repo = parts[-1]   # Last part is repo name
            branch = workspace.git_template.default_branch or 'main'
            template_path = workspace.git_template.language.lower() + '-template'
            
            logger.info(f"Downloading template: owner={owner}, repo={repo}, branch={branch}, template={template_path}")

            # Download template directory recursively
            success = self._download_directory_contents(owner, repo, template_path, branch, workspace_path)
            if success:
                logger.info(f"Successfully downloaded template for workspace {workspace.id}")
                contents = os.listdir(workspace_path)
                logger.info(f"Final workspace contents: {contents}")
                
                # Verify we only got the template files
                if '.git' in contents or any(x.endswith('-template') for x in contents):
                    logger.error("Found unexpected files in workspace!")
                    logger.error(f"Contents: {contents}")
                    shutil.rmtree(workspace_path)
                    return False
                
                return True
            else:
                logger.error(f"Failed to download template for workspace {workspace.id}")
                return False

        except Exception as e:
            logger.error(f"Error setting up workspace: {str(e)}")
            return False

    def pull_latest(self, workspace):
        """Pull latest changes for a workspace"""
        workspace_path = os.path.join(self.workspace_root, str(workspace.id))
        
        try:
            result = subprocess.run(
                ['git', 'pull'],
                cwd=workspace_path,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                logger.error(f"Git pull failed: {result.stderr}")
                return False
            return True
        except Exception as e:
            logger.exception(f"Error pulling changes: {e}")
            return False
