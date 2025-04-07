import { cn } from "@/lib/utils";
import { Box, Copy, Check } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { WorkspaceTerminal } from "./WorkspaceTerminal";

interface WorkspaceSetupProps {
  workspaceId: string;
  workspaceName: string;
  containerPassword?: string;
}

export function WorkspaceSetup({ workspaceId, workspaceName, containerPassword }: WorkspaceSetupProps) {
  const [copied, setCopied] = useState(false);

  const copyPassword = async () => {
    if (containerPassword) {
      await navigator.clipboard.writeText(containerPassword);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground p-6">
      <div className="flex flex-col items-center space-y-6 w-full max-w-2xl">
        <div className={cn(
          "relative",
          "after:absolute after:top-0 after:left-0",
          "after:w-full after:h-full",
          "after:animate-[pulse_2s_ease-in-out_infinite] after:bg-primary/10",
          "after:rounded-lg after:content-['']"
        )}>
          <Box className="w-12 h-12 text-primary relative z-10" />
        </div>
        <div className="space-y-2 text-center">
          <h1 className="text-2xl font-semibold">Setting up your workspace</h1>
          <p className="text-muted-foreground">{workspaceName}</p>
        </div>
        <div className="w-full space-y-6">
          <div className="space-y-1">
            <div className="h-1 w-full bg-muted rounded-full overflow-hidden">
              <div className="h-full bg-primary rounded-full animate-[progress_2s_ease-in-out_infinite]" />
            </div>
            <p className="text-xs text-muted-foreground text-center">Warming up...</p>
          </div>
          {containerPassword && (
            <div className="flex items-center gap-2 bg-muted/50 p-3 rounded-md">
              <div className="flex-1">
                <p className="text-xs text-muted-foreground mb-1">Workspace Password</p>
                <code className="text-sm font-mono">{containerPassword}</code>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={copyPassword}
                className="shrink-0"
              >
                {copied ? (
                  <Check className="h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
          )}
          <WorkspaceTerminal workspaceId={workspaceId} />
        </div>
      </div>
    </div>
  );
}
