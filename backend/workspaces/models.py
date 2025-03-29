from django.db import models
from django.conf import settings

# Create your models here.

class GitTemplate(models.Model):
    """Model for Git repository templates"""
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('typescript', 'TypeScript'),
        ('java', 'Java'),
        ('go', 'Go'),
        ('rust', 'Rust'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    repository_url = models.URLField()
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_public = models.BooleanField(default=True)
    default_branch = models.CharField(max_length=50, default='main')
    setup_commands = models.JSONField(default=list, help_text='List of commands to run after cloning')

    class Meta:
        ordering = ['language', 'name']

    def __str__(self):
        return f"{self.name} ({self.language})"

class ResourceClass(models.Model):
    """Model for workspace resource configurations"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cpu_count = models.IntegerField()
    ram_gb = models.IntegerField()
    disk_space_gb = models.IntegerField()
    gpu_count = models.IntegerField(default=0)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price_per_hour']
        verbose_name_plural = 'Resource classes'

    def __str__(self):
        return self.name

    @classmethod
    def get_default_class(cls):
        default_class, _ = cls.objects.get_or_create(
            name='Basic',
            defaults={
                'description': 'Basic resource configuration',
                'cpu_count': 2,
                'ram_gb': 4,
                'disk_space_gb': 20,
                'gpu_count': 0,
                'price_per_hour': 0.50
            }
        )
        return default_class.id

class Workspace(models.Model):
    """Model for user workspaces"""
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workspaces',
    )
    git_template = models.ForeignKey(
        GitTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    resource_class = models.ForeignKey(
        ResourceClass,
        on_delete=models.PROTECT,
        default=ResourceClass.get_default_class
    )
    
    # Container-related fields
    container_id = models.CharField(max_length=100, blank=True, null=True)
    container_status = models.CharField(max_length=20, default='created')
    container_url = models.URLField(blank=True, null=True)
    container_port = models.IntegerField(blank=True, null=True)
    container_password = models.CharField(max_length=100, blank=True, null=True)
    is_running = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.owner.username})"
