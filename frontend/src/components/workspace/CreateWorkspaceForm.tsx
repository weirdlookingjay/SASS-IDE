import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { GitTemplate, ResourceClass } from '@/types/workspace';
import { Code2, Database, Globe, FileCode, HardDrive, MemoryStick, Cpu } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CreateWorkspaceFormProps {
  templates: GitTemplate[];
  resources: ResourceClass[];
  onSubmit: (data: { name: string; git_template: number; resource_class: number }) => void;
  defaultTemplate?: GitTemplate;
}

const templateIcons: Record<string, React.ReactNode> = {
  'python': <Code2 className="h-4 w-4" />,
  'web': <Globe className="h-4 w-4" />,
  'database': <Database className="h-4 w-4" />,
  'java': <FileCode className="h-4 w-4" />,
  'javascript': <FileCode className="h-4 w-4" />,
  'typescript': <FileCode className="h-4 w-4" />,
  'rust': <FileCode className="h-4 w-4" />,
  'go': <FileCode className="h-4 w-4" />,
};

export function CreateWorkspaceForm({ templates, resources, onSubmit, defaultTemplate }: CreateWorkspaceFormProps) {
  const [name, setName] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(defaultTemplate?.id || null);
  const [selectedResource, setSelectedResource] = useState<number | null>(resources[0]?.id || null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !selectedTemplate || !selectedResource) return;

    onSubmit({
      name,
      git_template: selectedTemplate,
      resource_class: selectedResource,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="name">Workspace Name</Label>
        <Input
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="My Awesome Project"
          required
        />
      </div>

      <div className="space-y-2">
        <Label>Template</Label>
        <Select
          value={selectedTemplate?.toString()}
          onValueChange={(value) => setSelectedTemplate(Number(value))}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select a template" />
          </SelectTrigger>
          <SelectContent>
            {templates.map((template) => (
              <SelectItem key={template.id} value={template.id.toString()}>
                <div className="flex items-center gap-2">
                  <div className={cn(
                    "p-1 rounded",
                    template.language === 'python' ? "bg-yellow-500/10 text-yellow-500" :
                    template.language === 'web' ? "bg-blue-500/10 text-blue-500" :
                    template.language === 'java' ? "bg-orange-500/10 text-orange-500" :
                    template.language === 'rust' ? "bg-red-500/10 text-red-500" :
                    template.language === 'go' ? "bg-cyan-500/10 text-cyan-500" :
                    "bg-gray-500/10 text-gray-500"
                  )}>
                    {templateIcons[template.language.toLowerCase()] || <FileCode className="h-4 w-4" />}
                  </div>
                  <span>{template.name}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {selectedTemplate && (
          <div className="mt-2 text-sm text-muted-foreground">
            {templates.find(t => t.id === selectedTemplate)?.description}
          </div>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="resource">Resource Class</Label>
        <Select
          value={selectedResource?.toString()}
          onValueChange={(value) => setSelectedResource(Number(value))}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select a resource class" />
          </SelectTrigger>
          <SelectContent>
            {resources.map((resource) => (
              <SelectItem key={resource.id} value={resource.id.toString()}>
                <div className="space-y-1.5">
                  <div className="font-medium">{resource.name}</div>
                  <div className="text-xs text-muted-foreground flex items-center gap-2">
                    <span className="flex items-center gap-1">
                      <Cpu className="h-3 w-3" />
                      {resource.cpu_count} CPU
                    </span>
                    <span className="flex items-center gap-1">
                      <MemoryStick className="h-3 w-3" />
                      {resource.memory_gb}GB RAM
                    </span>
                    <span className="flex items-center gap-1">
                      <HardDrive className="h-3 w-3" />
                      {resource.disk_space_gb}GB Disk
                    </span>
                  </div>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Button type="submit" disabled={!name || !selectedTemplate || !selectedResource}>
        Create Workspace
      </Button>
    </form>
  );
}
