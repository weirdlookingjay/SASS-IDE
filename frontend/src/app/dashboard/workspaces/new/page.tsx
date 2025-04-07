'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { CreateWorkspaceForm } from '@/components/workspace/CreateWorkspaceForm';
import { TemplatesGallery } from '@/components/workspace/TemplatesGallery';
import { workspaces } from '@/utils/api';
import { GitTemplate, ResourceClass } from '@/types/workspace';
import { useAuth } from '@/hooks/useAuth';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function NewWorkspacePage() {
  const { user, isLoading: isAuthLoading } = useAuth();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [templates, setTemplates] = useState<GitTemplate[]>([]);
  const [resources, setResources] = useState<ResourceClass[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<GitTemplate | null>(null);
  const [activeTab, setActiveTab] = useState<string>("templates");

  useEffect(() => {
    if (isAuthLoading) return;
    if (!user) {
      router.push('/login');
      return;
    }

    async function fetchData() {
      try {
        setIsLoading(true);
        setError('');
        const [templatesRes, resourcesRes] = await Promise.all([
          workspaces.templates(),
          workspaces.resources(),
        ]);
        setTemplates(templatesRes);
        setResources(resourcesRes);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to load workspace options. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }

    fetchData();
  }, [user, isAuthLoading, router]);

  const handleCreateWorkspace = async (data: { name: string; git_template: number; resource_class: number }) => {
    try {
      setError('');
      await workspaces.create(data);
      router.push('/dashboard/workspaces');
    } catch (error) {
      console.error('Error creating workspace:', error);
      setError('Failed to create workspace. Please try again.');
    }
  };

  if (isLoading || isAuthLoading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/dashboard/workspaces">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <h1 className="text-2xl font-bold">Create New Workspace</h1>
      </div>

      {error && (
        <div className="bg-destructive/15 text-destructive px-4 py-3 rounded">
          {error}
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="templates">Choose Template</TabsTrigger>
          <TabsTrigger value="configure" disabled={!selectedTemplate}>
            Configure Workspace
          </TabsTrigger>
        </TabsList>

        <TabsContent value="templates" className="space-y-6">
          <TemplatesGallery
            templates={templates}
            onTemplateSelect={(template) => {
              setSelectedTemplate(template);
              setActiveTab("configure");
            }}
          />
        </TabsContent>

        <TabsContent value="configure">
          {selectedTemplate && (
            <CreateWorkspaceForm
              templates={templates}
              resources={resources}
              onSubmit={handleCreateWorkspace}
              defaultTemplate={selectedTemplate}
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
