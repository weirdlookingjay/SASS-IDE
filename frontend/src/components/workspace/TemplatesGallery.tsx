import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { GitTemplate } from '@/types/workspace';
import { Code2, Database, FileCode, Globe, Search } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface TemplatesGalleryProps {
  templates: GitTemplate[];
  onTemplateSelect: (template: GitTemplate) => void;
  className?: string;
}

const templateIcons: Record<string, React.ReactNode> = {
  'Python': <Code2 className="h-5 w-5" />,
  'Web': <Globe className="h-5 w-5" />,
  'Database': <Database className="h-5 w-5" />,
  'Custom': <FileCode className="h-5 w-5" />,
};

export function TemplatesGallery({ templates, onTemplateSelect, className }: TemplatesGalleryProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Get unique categories from templates
  const categories = ['all', ...new Set(templates.map(t => t.language))];

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || template.language === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className={cn("space-y-6", className)}>
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex gap-2 overflow-x-auto pb-2">
          {categories.map(category => (
            <Button
              key={category}
              variant={selectedCategory === category ? "default" : "outline"}
              onClick={() => setSelectedCategory(category)}
              className="whitespace-nowrap"
            >
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTemplates.map((template) => (
          <motion.div
            key={template.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="h-full flex flex-col hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start gap-3">
                  <div className={cn(
                    "p-2 rounded-lg",
                    template.language === 'python' ? "bg-yellow-500/10 text-yellow-500" :
                    template.language === 'web' ? "bg-blue-500/10 text-blue-500" :
                    template.language === 'database' ? "bg-green-500/10 text-green-500" :
                    "bg-gray-500/10 text-gray-500"
                  )}>
                    {templateIcons[template.language] || templateIcons['Custom']}
                  </div>
                  <div className="space-y-1">
                    <CardTitle>{template.name}</CardTitle>
                    <CardDescription className="text-xs">
                      {template.language.charAt(0).toUpperCase() + template.language.slice(1)}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="flex-1">
                <p className="text-sm text-muted-foreground">
                  {template.description}
                </p>
              </CardContent>
              <CardFooter>
                <Button 
                  variant="default" 
                  className="w-full"
                  onClick={() => onTemplateSelect(template)}
                >
                  Use Template
                </Button>
              </CardFooter>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
