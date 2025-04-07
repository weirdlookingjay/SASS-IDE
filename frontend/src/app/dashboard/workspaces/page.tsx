'use client';

import { useEffect, useState, useMemo, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Workspace, WorkspaceStatus } from '@/types/workspace';
import { workspaces as workspaceApi } from '@/utils/api';
import { useAuth } from '@/hooks/useAuth';
import { 
  Copy, 
  Plus,
  Terminal,
  MonitorPlay,
  Trash2,
  Clock,
  Calendar,
  Cpu,
  HardDrive,
  MemoryStick,
  Code2,
  FileCode,
  Globe,
  Database,
  ChevronDown,
  ChevronUp,
  Boxes,
  GitBranch,
  Users
} from 'lucide-react';
import { toast } from 'sonner';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

// Template icons mapping
const templateIcons: Record<string, React.ReactNode> = {
  'Python': <Code2 className="h-5 w-5" />,
  'Web': <Globe className="h-5 w-5" />,
  'Database': <Database className="h-5 w-5" />,
  'Custom': <FileCode className="h-5 w-5" />,
};

// Template-specific information
const templateDetails: Record<string, { 
  icon: React.ReactNode;
  description: string;
  features: string[];
  recommendedResources: {
    cpu: number;
    memory: number;
    disk: number;
  };
}> = {
  'Python': {
    icon: <Code2 className="h-5 w-5" />,
    description: 'Python development environment with popular data science packages',
    features: ['Jupyter Notebooks', 'NumPy', 'Pandas', 'Scikit-learn'],
    recommendedResources: {
      cpu: 2,
      memory: 4096,
      disk: 10
    }
  },
  'Web': {
    icon: <Globe className="h-5 w-5" />,
    description: 'Full-stack web development environment',
    features: ['Node.js', 'React', 'Next.js', 'PostgreSQL'],
    recommendedResources: {
      cpu: 2,
      memory: 4096,
      disk: 20
    }
  },
  'Database': {
    icon: <Database className="h-5 w-5" />,
    description: 'Database development and administration environment',
    features: ['PostgreSQL', 'MongoDB', 'Redis', 'GUI Tools'],
    recommendedResources: {
      cpu: 4,
      memory: 8192,
      disk: 50
    }
  },
  'Custom': {
    icon: <FileCode className="h-5 w-5" />,
    description: 'Custom development environment',
    features: ['Customizable', 'Flexible', 'Your Choice of Tools'],
    recommendedResources: {
      cpu: 2,
      memory: 4096,
      disk: 20
    }
  }
};

// Status color mapping
const statusColors: Record<WorkspaceStatus, { bg: string; text: string; icon: string }> = {
  'Running': { bg: 'bg-green-500/10', text: 'text-green-500', icon: 'text-green-500' },
  'Stopped': { bg: 'bg-gray-500/10', text: 'text-gray-500', icon: 'text-gray-500' },
  'Error': { bg: 'bg-red-500/10', text: 'text-red-500', icon: 'text-red-500' },
};

interface UserDetails {
  username: string;
  first_name: string;
  last_name: string;
  email: string;
}

export default function WorkspacesPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [error, setError] = useState('');
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | WorkspaceStatus>('all');
  const [templateFilter, setTemplateFilter] = useState<string>('all');
  const [workspaceToDelete, setWorkspaceToDelete] = useState<Workspace | null>(null);
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [selectedWorkspace, setSelectedWorkspace] = useState<Workspace | null>(null);
  const [openCollapsibles, setOpenCollapsibles] = useState<Record<string, boolean>>({});
  const [userDetails, setUserDetails] = useState<Record<string, UserDetails>>({});
  const { user, isAdmin, isLoading } = useAuth();



  // Get workspace stats
  const workspaceStats = useMemo(() => {
    const total = workspaces.length;
    const running = workspaces.filter(w => w.status === 'Running').length;
    const stopped = workspaces.filter(w => w.status === 'Stopped').length;
    const error = workspaces.filter(w => w.status === 'Error').length;
    return { total, running, stopped, error };
  }, [workspaces]);

  // Get unique template types
  const templateTypes = useMemo(() => {
    const types = new Set(workspaces.map(w => w.git_template_details?.name || 'Custom'));
    return ['all', ...Array.from(types)];
  }, [workspaces]);

  // Filter and sort workspaces
  const filteredWorkspaces = useMemo(() => {
    return workspaces
      .filter(workspace => {
        const matchesSearch = searchQuery === '' || 
          workspace.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (workspace.git_template_details?.name || 'Custom').toLowerCase().includes(searchQuery.toLowerCase());
        
        const matchesStatus = statusFilter === 'all' || workspace.status === statusFilter;
        
        const matchesTemplate = templateFilter === 'all' || 
          (workspace.git_template_details?.name || 'Custom') === templateFilter;

        // Only show workspaces owned by user or if user is admin
        const hasPermission = user?.username === workspace.owner_username || isAdmin;

        return matchesSearch && matchesStatus && matchesTemplate && hasPermission;
      })
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [workspaces, searchQuery, statusFilter, templateFilter, user?.username, isAdmin]);

  const fetchWorkspaces = useCallback(async () => {
    try {
      const response = await workspaceApi.list();
      const normalizedWorkspaces = response.data.map(workspace => ({
        ...workspace,
        status: workspace.status || 'Stopped'
      }));
      console.log('Fetched workspaces:', normalizedWorkspaces);
      setWorkspaces(normalizedWorkspaces);
      setError('');
    } catch (err: unknown) {
      const error = err as { response?: { status: number } };
      console.error('Failed to fetch workspaces:', error);
      setError('Failed to fetch workspaces');
      if (error.response?.status === 401) {
        console.log('Unauthorized, redirecting to login');
        router.replace('/login');
      }
    }
  }, [router]);

  useEffect(() => {
    // Only fetch workspaces if we have a user and auth is not loading
    if (user && !isLoading) {
      fetchWorkspaces();
    }
  }, [fetchWorkspaces, user, isLoading]);

  const fetchUserDetails = useCallback(async (userId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        console.warn('No auth token available');
        return;
      }

      const response = await fetch(`${apiUrl}/api/jwt/users/${userId}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        console.warn(`User ${userId} not found or unauthorized`);
        return;
      }
      
      const data = await response.json();
      console.log('User details response:', data); // Debug log
      setUserDetails(prev => ({
        ...prev,
        [userId]: {
          username: data.username,
          first_name: data.first_name,
          last_name: data.last_name,
          email: data.email
        }
      }));
    } catch (error) {
      console.error('Error fetching user details:', error);
    }
  }, []);

  // Fetch user details when workspaces change
  useEffect(() => {
    const missingUsers = workspaces
      .map(workspace => workspace.owner_username)
      .filter((username, index, self) => 
        // Remove duplicates
        self.indexOf(username) === index && 
        // Only fetch if we don't have the details
        !userDetails[username]
      );

    missingUsers.forEach(username => {
      fetchUserDetails(username);
    });
  }, [workspaces, userDetails, fetchUserDetails]);

  const handleStartStop = async (workspace: Workspace) => {
    try {
      if (workspace.status === 'Running') {
        await workspaceApi.stop(workspace.id.toString());
        setWorkspaces(workspaces.map(w => 
          w.id.toString() === workspace.id.toString() ? { ...w, status: 'Stopped' as const } : w
        ));
        toast.success('Workspace stopped successfully');
      } else {
        await workspaceApi.start(workspace.id.toString());
        // Redirect to the workspace setup page
        window.location.href = `/dashboard/workspaces/${workspace.id}`;
      }
    } catch (err) {
      toast.error(workspace.status === 'Running' ? 'Failed to stop workspace' : 'Failed to start workspace');
      console.error('Error updating workspace:', err);
    }
  };

  const handleOpen = async (workspace: Workspace) => {
    try {
      // If workspace is not running, redirect to setup page
      if (workspace.status !== 'Running') {
        window.location.href = `/dashboard/workspaces/${workspace.id}`;
        return;
      }
      
      // If running, show password dialog
      setSelectedWorkspace(workspace);
      setPasswordDialogOpen(true);
    } catch (err) {
      toast.error('Failed to open workspace', {
        description: 'Please try again or contact support if the issue persists.'
      });
      console.error('Error opening workspace:', err);
    }
  };

  const handleDelete = async (workspace: Workspace) => {
    setWorkspaceToDelete(workspace);
  };

  const confirmDelete = async () => {
    if (!workspaceToDelete) return;

    try {
      await workspaceApi.delete(workspaceToDelete.id.toString());
      setWorkspaces(workspaces.filter(w => w.id.toString() !== workspaceToDelete.id.toString()));
      toast.success('Workspace deleted successfully');
      setWorkspaceToDelete(null);
    } catch (err) {
      toast.error('Failed to delete workspace');
      console.error('Error deleting workspace:', err);
    }
  };

  const openWorkspaceInBrowser = () => {
    if (selectedWorkspace?.container_url) {
      // Make sure container is ready
      if (selectedWorkspace.status === 'Running') {
        const url = selectedWorkspace.container_url;
        window.open(url, '_blank', 'noopener,noreferrer');
        setPasswordDialogOpen(false);
      } else {
        toast.error('Workspace is not ready', {
          description: 'Please wait a few moments for the workspace to start.'
        });
      }
    } else {
      toast.error('No workspace URL available', {
        description: 'Please try refreshing the page.'
      });
    }
  };

  const copyPasswordToClipboard = async () => {
    if (selectedWorkspace?.container_password) {
      try {
        await navigator.clipboard.writeText(selectedWorkspace.container_password);
        toast.success('Password copied to clipboard', {
          description: 'The workspace password has been copied to your clipboard.'
        });
      } catch {
        toast.error('Failed to copy password', {
          description: 'Please try copying the password manually.'
        });
      }
    }
  };

  const toggleCollapsible = (workspaceId: string) => {
    setOpenCollapsibles(prev => ({
      ...prev,
      [workspaceId]: !prev[workspaceId]
    }));
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Workspace Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Total Workspaces</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{workspaceStats.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Running</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{workspaceStats.running}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Stopped</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-600">{workspaceStats.stopped}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Error</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{workspaceStats.error}</div>
            </CardContent>
          </Card>
        </div>

        {/* Toolbar */}
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between bg-card p-4 rounded-lg border">
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
            <Input
              placeholder="Search workspaces..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full md:w-[300px]"
            />
            <Select value={statusFilter} onValueChange={(value: 'all' | WorkspaceStatus) => setStatusFilter(value)}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="Running">Running</SelectItem>
                <SelectItem value="Stopped">Stopped</SelectItem>
                <SelectItem value="Error">Error</SelectItem>
              </SelectContent>
            </Select>
            <Select value={templateFilter} onValueChange={setTemplateFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by template" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Templates</SelectItem>
                {templateTypes.slice(1).map((type) => (
                  <SelectItem key={type} value={type}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex gap-2">
            <Link href="/dashboard/workspaces/new">
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                New Workspace
              </Button>
            </Link>
          </div>
        </div>

        {error && (
          <div className="bg-destructive/15 text-destructive px-4 py-2 rounded-lg">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredWorkspaces.map((workspace) => (
            <motion.div 
              key={workspace.id} 
              className="flex flex-col h-full group"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Card>
                <CardHeader className="flex flex-col space-y-4">
                  <div className="flex justify-between items-start w-full">
                    <div className="flex items-start gap-3">
                      <motion.div 
                        className={cn(
                          "p-2 rounded-lg",
                          statusColors[workspace.status].bg
                        )}
                        animate={{ 
                          backgroundColor: workspace.status === 'Running' ? 'rgba(34, 197, 94, 0.1)' : 
                                        workspace.status === 'Stopped' ? 'rgba(107, 114, 128, 0.1)' : 
                                        'rgba(239, 68, 68, 0.1)'
                        }}
                        transition={{ duration: 0.3 }}
                      >
                        {templateIcons[workspace.git_template_details?.name || 'Custom']}
                      </motion.div>
                      <div className="space-y-1.5">
                        <CardTitle className="text-xl font-semibold">{workspace.name}</CardTitle>
                        <CardDescription className="text-sm text-muted-foreground">
                          {workspace.git_template_details?.name 
                            ? templateDetails[workspace.git_template_details.name]?.description || 'Custom template'
                            : templateDetails['Custom'].description}
                        </CardDescription>
                      </div>
                    </div>
                    <motion.div
                      animate={{ scale: workspace.status === 'Running' ? 1.1 : 1 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Badge 
                        variant="outline"
                        className={cn(
                          "capitalize transition-colors",
                          statusColors[workspace.status].text,
                          statusColors[workspace.status].bg
                        )}
                      >
                        {workspace.status}
                      </Badge>
                    </motion.div>
                  </div>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col justify-between">
                  <div className="space-y-4">
                    {/* Resource Usage */}
                    {workspace.status === 'Running' && workspace.resource_usage && (
                      <div className="space-y-3">
                        <TooltipProvider>
                          <div className="space-y-2">
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <div className="flex justify-between text-sm">
                                  <span className="flex items-center gap-2">
                                    <Cpu className="h-4 w-4" />
                                    CPU
                                  </span>
                                  <span>{Math.round(workspace.resource_usage.cpu_usage)}%</span>
                                </div>
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>CPU Usage: {Math.round(workspace.resource_usage.cpu_usage)}%</p>
                                <p>Recommended: {templateDetails[workspace.git_template_details?.name || 'Custom'].recommendedResources.cpu} cores</p>
                              </TooltipContent>
                            </Tooltip>
                            <Progress value={Number(workspace.resource_usage.cpu_usage)} />
                          </div>

                          <div className="space-y-2">
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <div className="flex justify-between text-sm">
                                  <span className="flex items-center gap-2">
                                    <MemoryStick className="h-4 w-4" />
                                    Memory
                                  </span>
                                  <span>
                                    {Math.round(workspace.resource_usage.memory_usage)}%
                                    ({Math.round(workspace.resource_usage.memory_total / 1024)} GB)
                                  </span>
                                </div>
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Memory Usage: {Math.round(workspace.resource_usage.memory_usage)}%</p>
                                <p>Total Memory: {Math.round(workspace.resource_usage.memory_total / 1024)} GB</p>
                                <p>Recommended: {templateDetails[workspace.git_template_details?.name || 'Custom'].recommendedResources.memory / 1024} GB</p>
                              </TooltipContent>
                            </Tooltip>
                            <Progress value={Number(workspace.resource_usage.memory_usage)} />
                          </div>

                          <div className="space-y-2">
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <div className="flex justify-between text-sm">
                                  <span className="flex items-center gap-2">
                                    <HardDrive className="h-4 w-4" />
                                    Disk
                                  </span>
                                  <span>
                                    {Math.round(workspace.resource_usage.disk_usage)}%
                                    ({workspace.resource_usage.disk_total} GB)
                                  </span>
                                </div>
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Disk Usage: {Math.round(workspace.resource_usage.disk_usage)}%</p>
                                <p>Total Disk: {workspace.resource_usage.disk_total} GB</p>
                                <p>Recommended: {templateDetails[workspace.git_template_details?.name || 'Custom'].recommendedResources.disk} GB</p>
                              </TooltipContent>
                            </Tooltip>
                            <Progress value={Number(workspace.resource_usage.disk_usage)} />
                          </div>
                        </TooltipProvider>
                      </div>
                    )}
                    {/* Template Details */}
                    <Collapsible 
                      className="mt-4" 
                      open={openCollapsibles[workspace.id] ?? false} 
                      onOpenChange={() => toggleCollapsible(workspace.id)}
                    >
                      <CollapsibleTrigger className="flex justify-between items-center w-full text-sm hover:text-primary transition-colors">
                        <span>Template Details</span>
                        {openCollapsibles[workspace.id] ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )}
                      </CollapsibleTrigger>
                      <CollapsibleContent className="mt-2 space-y-4">
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.2 }}
                        >
                          <div className="space-y-4">
                            <div className="flex justify-between text-sm">
                              <span className="flex items-center gap-2">
                                <GitBranch className="h-4 w-4" />
                                Template
                              </span>
                              <span>{workspace.git_template_details?.name || 'Custom'}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="flex items-center gap-2">
                                <Users className="h-4 w-4" />
                                Owner
                              </span>
                              <span>
                                {workspace.owner_username}
                              </span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="flex items-center gap-2">
                                <Boxes className="h-4 w-4" />
                                Features
                              </span>
                              <span>
                                {workspace.git_template_details?.name 
                                  ? templateDetails[workspace.git_template_details.name]?.features.join(', ') || 'Custom features'
                                  : templateDetails['Custom'].features.join(', ')}
                              </span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="flex items-center gap-2">
                                <Cpu className="h-4 w-4" />
                                Recommended CPU
                              </span>
                              <span>
                                {workspace.git_template_details?.name 
                                  ? templateDetails[workspace.git_template_details.name]?.recommendedResources.cpu || '2'
                                  : templateDetails['Custom'].recommendedResources.cpu} cores
                              </span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="flex items-center gap-2">
                                <MemoryStick className="h-4 w-4" />
                                Recommended Memory
                              </span>
                              <span>
                                {workspace.git_template_details?.name 
                                  ? templateDetails[workspace.git_template_details.name]?.recommendedResources.memory || '4096'
                                  : templateDetails['Custom'].recommendedResources.memory} MB
                              </span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="flex items-center gap-2">
                                <HardDrive className="h-4 w-4" />
                                Recommended Disk
                              </span>
                              <span>
                                {workspace.git_template_details?.name 
                                  ? templateDetails[workspace.git_template_details.name]?.recommendedResources.disk || '20'
                                  : templateDetails['Custom'].recommendedResources.disk} GB
                              </span>
                            </div>
                          </div>
                        </motion.div>
                      </CollapsibleContent>
                    </Collapsible>

                    {/* Metadata */}
                    <div className="grid grid-cols-2 gap-2">
                      <div className="text-sm text-muted-foreground">
                        <span className="flex items-center gap-2 font-medium">
                          <Clock className="h-4 w-4" />
                          Last Accessed
                        </span>
                        {workspace.last_accessed && new Date(workspace.last_accessed).getTime() > 0 ? (
                          formatDistanceToNow(new Date(workspace.last_accessed), { addSuffix: true })
                        ) : (
                          'Never'
                        )}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        <span className="flex items-center gap-2 font-medium">
                          <Calendar className="h-4 w-4" />
                          Created
                        </span>
                        {workspace.created_at && new Date(workspace.created_at).getTime() > 0 ? (
                          formatDistanceToNow(new Date(workspace.created_at), { addSuffix: true })
                        ) : (
                          'Unknown'
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <motion.div 
                    className="flex justify-end gap-2 mt-4"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    whileHover={{ scale: 1.02 }}
                  >
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleStartStop(workspace)}
                            className="hover:scale-105 transition-transform"
                          >
                            {workspace.status === 'Running' ? (
                              <motion.div
                                initial={{ scale: 0.8 }}
                                animate={{ scale: 1 }}
                                className="flex items-center"
                              >
                                <Terminal className="h-4 w-4 mr-2" />
                                Stop
                              </motion.div>
                            ) : (
                              <motion.div
                                initial={{ scale: 0.8 }}
                                animate={{ scale: 1 }}
                                className="flex items-center"
                              >
                                <MonitorPlay className="h-4 w-4 mr-2" />
                                Start
                              </motion.div>
                            )}
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                          {workspace.status === 'Running' ? 'Stop this workspace' : 'Start this workspace'}
                        </TooltipContent>
                      </Tooltip>

                      {workspace.status === 'Running' && (
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              variant="default"
                              size="sm"
                              onClick={() => handleOpen(workspace)}
                              className="hover:scale-105 transition-transform"
                            >
                              <motion.div
                                initial={{ scale: 0.8 }}
                                animate={{ scale: 1 }}
                                className="flex items-center"
                              >
                                <MonitorPlay className="h-4 w-4 mr-2" />
                                Open
                              </motion.div>
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            Open this workspace in a new window
                          </TooltipContent>
                        </Tooltip>
                      )}

                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => handleDelete(workspace)}
                            className="hover:scale-105 transition-transform"
                          >
                            <motion.div
                              initial={{ scale: 0.8 }}
                              animate={{ scale: 1 }}
                              className="flex items-center"
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete
                            </motion.div>
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>
                          Permanently delete this workspace
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </motion.div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>

      <Dialog open={!!workspaceToDelete} onOpenChange={() => setWorkspaceToDelete(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Workspace</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete workspace &quot;{workspaceToDelete?.name}&quot;? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-3 mt-6">
            <Button variant="outline" onClick={() => setWorkspaceToDelete(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={() => confirmDelete()}>
              Delete
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={passwordDialogOpen} onOpenChange={setPasswordDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Workspace Password</DialogTitle>
            <DialogDescription>
              Use this password to access your workspace. Make sure to save it.
            </DialogDescription>
          </DialogHeader>
          <div className="flex items-center gap-2">
            <Input
              value={selectedWorkspace?.container_password || ''}
              readOnly
              className="font-mono"
            />
            <Button
              variant="outline"
              size="icon"
              onClick={copyPasswordToClipboard}
              className="h-8 w-8"
            >
              <Copy className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex justify-end gap-3 mt-6">
            <Button variant="outline" onClick={() => setPasswordDialogOpen(false)}>
              Close
            </Button>
            <Button variant="default" onClick={openWorkspaceInBrowser}>
              Open Workspace
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
