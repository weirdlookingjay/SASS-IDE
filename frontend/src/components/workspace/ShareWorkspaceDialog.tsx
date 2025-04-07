import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Workspace } from '@/types/workspace';
import { Users, Link as LinkIcon, Copy } from 'lucide-react';
import { toast } from 'sonner';

interface ShareWorkspaceDialogProps {
  workspace: Workspace;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onShare: (data: { username: string; accessLevel: 'read' | 'write' }) => Promise<void>;
}

export function ShareWorkspaceDialog({ workspace, open, onOpenChange, onShare }: ShareWorkspaceDialogProps) {
  const [username, setUsername] = useState('');
  const [accessLevel, setAccessLevel] = useState<'read' | 'write'>('read');
  const [isPublic, setIsPublic] = useState(workspace.is_public || false);
  const [isLoading, setIsLoading] = useState(false);

  const handleShare = async () => {
    if (!username) return;
    
    try {
      setIsLoading(true);
      await onShare({ username, accessLevel });
      setUsername('');
      toast.success('Workspace shared', {
        description: `Successfully shared with ${username}`,
      });
    } catch (error) {
      toast.error('Error', {
        description: 'Failed to share workspace. Please try again.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const copyShareLink = () => {
    const shareUrl = `${window.location.origin}/workspace/${workspace.id}`;
    navigator.clipboard.writeText(shareUrl);
    toast.success('Link copied', {
      description: 'Share link copied to clipboard',
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Share Workspace</DialogTitle>
          <DialogDescription>
            Share your workspace with other users or make it public
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          <div className="flex items-center justify-between space-x-2">
            <div className="space-y-1">
              <Label>Public Access</Label>
              <div className="text-sm text-muted-foreground">
                Allow anyone with the link to view this workspace
              </div>
            </div>
            <Switch
              checked={isPublic}
              onCheckedChange={setIsPublic}
              aria-label="Toggle public access"
            />
          </div>

          <div className="space-y-4">
            <Label>Share with User</Label>
            <div className="flex space-x-2">
              <div className="flex-1">
                <Input
                  placeholder="Enter username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <Button onClick={handleShare} disabled={!username || isLoading}>
                Share
              </Button>
            </div>
            <div className="flex items-center space-x-2">
              <Label className="text-sm font-normal">Access Level:</Label>
              <Button
                variant={accessLevel === 'read' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setAccessLevel('read')}
              >
                Read
              </Button>
              <Button
                variant={accessLevel === 'write' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setAccessLevel('write')}
              >
                Write
              </Button>
            </div>
          </div>

          {workspace.shared_with && workspace.shared_with.length > 0 && (
            <div className="space-y-4">
              <Label>Shared With</Label>
              <div className="space-y-2">
                {workspace.shared_with.map((user) => (
                  <div key={user.username} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Users className="h-4 w-4" />
                      <span>{user.username}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {/* TODO: Implement remove share */}}
                    >
                      Remove
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="space-y-4">
            <Label>Share Link</Label>
            <div className="flex space-x-2">
              <Input
                readOnly
                value={`${window.location.origin}/workspace/${workspace.id}`}
              />
              <Button size="icon" variant="outline" onClick={copyShareLink}>
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
