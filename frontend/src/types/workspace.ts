export interface GitTemplate {
  id: number;
  name: string;
  description: string;
  language: string;
  repository_url: string;
  icon?: string;
}

export interface ResourceClass {
  id: number;
  name: string;
  cpu_count: number;
  memory_gb: number;
  description: string;
  disk_space_gb: number;
  gpu_count: number;
  price_per_hour: string;
}

export type WorkspaceStatus = 'Running' | 'Stopped' | 'Error';

export type ContainerStatus = 'created' | 'starting' | 'running' | 'stopped' | 'failed';

export interface SharedUser {
  username: string;
  access_level: 'read' | 'write';
  shared_at: string;
}

export interface Workspace {
  id: string;
  name: string;
  owner_username: string;
  status: WorkspaceStatus;
  container_status: ContainerStatus;
  created_at: string;
  last_accessed: string;
  is_public: boolean;
  shared_with: SharedUser[];
  container_url?: string;
  container_password?: string;
  git_template_details?: {
    name: string;
    language: string;
    icon?: string;
  };
  resource_usage?: {
    cpu_usage: number;
    memory_usage: number;
    memory_total: number;
    disk_usage: number;
    disk_total: number;
  };
}

export interface WorkspaceType {
  id: string;
  name: string;
  owner: string;
  status: 'running' | 'stopped';
  created_at: string;
  last_accessed: string;
  container_url?: string;
  container_password?: string;
  git_template_details?: {
    name: string;
    language: string;
    icon?: string;
  };
  resource_usage?: {
    cpu_usage: number;
    memory_usage: number;
    memory_total: number;
    disk_usage: number;
    disk_total: number;
  };
}
