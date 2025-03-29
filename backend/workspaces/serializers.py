from rest_framework import serializers
from .models import GitTemplate, ResourceClass, Workspace

class GitTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitTemplate
        fields = [
            'id', 'name', 'description', 'repository_url', 'language',
            'created_at', 'updated_at', 'created_by', 'is_public',
            'default_branch', 'setup_commands'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        # Set the created_by field to the current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class ResourceClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceClass
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class WorkspaceSerializer(serializers.ModelSerializer):
    git_template_details = GitTemplateSerializer(source='git_template', read_only=True)
    resource_class_details = ResourceClassSerializer(source='resource_class', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'owner', 'owner_username',
            'git_template', 'git_template_details',
            'resource_class', 'resource_class_details',
            'container_id', 'container_status', 'container_url',
            'container_port', 'container_password', 'is_running',
            'last_accessed', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'owner', 'container_id', 'container_status',
            'container_url', 'container_port', 'container_password',
            'is_running', 'last_accessed', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        # Set the owner to the current user
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
