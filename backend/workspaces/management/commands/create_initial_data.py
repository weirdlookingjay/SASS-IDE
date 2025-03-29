from django.core.management.base import BaseCommand
from workspaces.models import GitTemplate, ResourceClass

class Command(BaseCommand):
    help = 'Creates initial data for testing'

    def handle(self, *args, **kwargs):
        # Create Git templates
        templates = [
            {
                'name': 'Python Basic',
                'repository_url': 'https://github.com/example/python-template',
                'description': 'Basic Python development environment',
                'language': 'python',
            },
            {
                'name': 'Node.js TypeScript',
                'repository_url': 'https://github.com/example/node-typescript-template',
                'description': 'Node.js with TypeScript configuration',
                'language': 'typescript',
            },
        ]

        for template in templates:
            GitTemplate.objects.get_or_create(
                name=template['name'],
                defaults=template
            )
            self.stdout.write(f"Created template: {template['name']}")

        # Create resource classes
        resources = [
            {
                'name': 'Basic',
                'cpu_count': 2,
                'ram_gb': 4,
                'disk_space_gb': 20,
                'gpu_count': 0,
                'price_per_hour': '0.50',
            },
            {
                'name': 'Standard',
                'cpu_count': 4,
                'ram_gb': 8,
                'disk_space_gb': 50,
                'gpu_count': 0,
                'price_per_hour': '1.00',
            },
            {
                'name': 'Professional',
                'cpu_count': 8,
                'ram_gb': 16,
                'disk_space_gb': 100,
                'gpu_count': 1,
                'price_per_hour': '2.50',
            },
        ]

        for resource in resources:
            ResourceClass.objects.get_or_create(
                name=resource['name'],
                defaults=resource
            )
            self.stdout.write(f"Created resource class: {resource['name']}")

        self.stdout.write(self.style.SUCCESS('Successfully created initial data'))
