'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { workspaces } from '@/utils/api';
import { Workspace } from '@/types/workspace';
import { WorkspaceSetup } from '@/components/workspace/WorkspaceSetup';

export default function WorkspacePage() {
  const params = useParams();
  const id = params?.id as string;
  
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchWorkspace() {
      try {
        setIsLoading(true);
        setError('');
        const response = await workspaces.get(id);
        const data = response.data as Workspace;
        setWorkspace(data);
        if (data.container_status === 'starting') {
          setIsStarting(true);
          // Poll for status changes
          const interval = setInterval(async () => {
            const updatedResponse = await workspaces.get(id);
            const updated = updatedResponse.data as Workspace;
            if (updated.container_status === 'running' || updated.container_password) {
              if (updated.container_status === 'running') {
                setIsStarting(false);
                clearInterval(interval);
                if (updated.container_url) {
                  window.open(updated.container_url, '_blank');
                }
              }
              setWorkspace(updated);
            } else if (updated.container_status === 'failed') {
              setIsStarting(false);
              setError('Failed to start workspace');
              clearInterval(interval);
            }
          }, 2000);
          return () => clearInterval(interval);
        } else if (data.container_status === 'running' && data.container_url) {
          const newWindow = window.open(data.container_url, '_blank');
          if (newWindow) {
            // Only redirect if window opened successfully
            setTimeout(() => {
              window.location.href = '/dashboard/workspaces';
            }, 500);
          }
        }
      } catch (error) {
        console.error('Error fetching workspace:', error);
        setError('Failed to load workspace');
      } finally {
        setIsLoading(false);
      }
    }
    if (id) {
      fetchWorkspace();
    }
  }, [id]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  if (!workspace) {
    return <div>Workspace not found</div>;
  }

  if (isStarting) {
    return <WorkspaceSetup 
      workspaceId={id} 
      workspaceName={workspace.name}
      containerPassword={workspace.container_password}
    />;
  }

  return (
    <div>
      <h1>{workspace.name}</h1>
      {/* Add more workspace details and controls here */}
    </div>
  );
}
