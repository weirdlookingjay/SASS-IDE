from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from workspaces.models import GitTemplate

User = get_user_model()

class Command(BaseCommand):
    help = 'Create initial Git templates for different programming languages'

    def handle(self, *args, **kwargs):
        # Get or create admin user
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            self.stdout.write('No admin user found. Please create one first.')
            return

        templates = [
            {
                'name': 'Python Basic',
                'description': 'Basic Python development environment with common tools and libraries',
                'repository_url': 'https://github.com/example/python-template',
                'language': 'python',
                'setup_commands': [
                    'python -m venv venv',
                    'source venv/bin/activate',
                    'pip install -r requirements.txt'
                ]
            },
            {
                'name': 'Node.js/JavaScript',
                'description': 'JavaScript development environment with Node.js and npm',
                'repository_url': 'https://github.com/example/javascript-template',
                'language': 'javascript',
                'setup_commands': [
                    'npm install'
                ]
            },
            {
                'name': 'TypeScript Project',
                'description': 'TypeScript development environment with Node.js and npm',
                'repository_url': 'https://github.com/example/typescript-template',
                'language': 'typescript',
                'setup_commands': [
                    'npm install',
                    'npm run build'
                ]
            },
            {
                'name': 'Java Spring Boot',
                'description': 'Java development environment with Spring Boot',
                'repository_url': 'https://github.com/example/java-template',
                'language': 'java',
                'setup_commands': [
                    './mvnw clean install'
                ]
            },
            {
                'name': 'Go Basic',
                'description': 'Go development environment with basic setup',
                'repository_url': 'https://github.com/example/go-template',
                'language': 'go',
                'setup_commands': [
                    'go mod download'
                ]
            },
            {
                'name': 'Rust Project',
                'description': 'Rust development environment with Cargo',
                'repository_url': 'https://github.com/example/rust-template',
                'language': 'rust',
                'setup_commands': [
                    'cargo build'
                ]
            }
        ]

        for template_data in templates:
            template, created = GitTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'description': template_data['description'],
                    'repository_url': template_data['repository_url'],
                    'language': template_data['language'],
                    'setup_commands': template_data['setup_commands'],
                    'created_by': admin
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created template: {template.name}'))
            else:
                self.stdout.write(f'Template already exists: {template.name}')
