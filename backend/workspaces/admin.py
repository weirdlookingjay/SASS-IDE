from django.contrib import admin
from .models import GitTemplate, ResourceClass, Workspace

# Register your models here.

@admin.register(GitTemplate)
class GitTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'created_at')
    list_filter = ('language',)
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(ResourceClass)
class ResourceClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'cpu_count', 'ram_gb', 'disk_space_gb', 'gpu_count', 'price_per_hour')
    list_filter = ('gpu_count',)
    search_fields = ('name',)
    ordering = ('price_per_hour',)

@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'git_template', 'resource_class', 'container_status', 'is_running', 'created_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('is_running', 'container_status', 'git_template', 'resource_class')
    readonly_fields = ('container_id', 'container_port', 'last_accessed', 'created_at', 'updated_at')
