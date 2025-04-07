import { useEffect, useRef, useState } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { workspaces } from '@/utils/api';

interface WorkspaceTerminalProps {
  workspaceId: string;
}

interface LogLine {
  timestamp: string;
  message: string;
  type: 'info' | 'error' | 'success';
}

export function WorkspaceTerminal({ workspaceId }: WorkspaceTerminalProps) {
  const [logs, setLogs] = useState<LogLine[]>([]);
  const [error, setError] = useState<string>();
  const scrollRef = useRef<HTMLDivElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | undefined>(undefined);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const logs = await workspaces.logs(workspaceId);
        if (logs) {
          const newLogs = logs.map((line: string) => {
            // Parse log line to extract timestamp and type
            const match = line.match(/\[(.*?)\]\s*(INFO|ERROR|SUCCESS)?\s*(.*)/);
            if (match) {
              const [, timestamp, type, message] = match;
              return {
                timestamp,
                message: message || line,
                type: (type?.toLowerCase() as 'info' | 'error' | 'success') || 'info'
              };
            }
            return {
              timestamp: new Date().toISOString(),
              message: line,
              type: 'info' as const
            };
          });

          setLogs(prev => {
            // Only add new logs that we haven't seen before
            const lastLog = prev[prev.length - 1];
            const startIndex = lastLog 
              ? newLogs.findIndex(log => 
                  log.timestamp > lastLog.timestamp || 
                  (log.timestamp === lastLog.timestamp && log.message !== lastLog.message)
                )
              : 0;
            
            return startIndex === -1 
              ? prev 
              : [...prev, ...newLogs.slice(startIndex)];
          });
        }
      } catch (error) {
        console.error('Error fetching logs:', error);
        setError('Failed to fetch logs');
      }
    };

    // Initial fetch
    fetchLogs();

    // Poll for new logs every second
    intervalRef.current = setInterval(fetchLogs, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [workspaceId]);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <ScrollArea 
      className="h-[300px] w-full rounded-md border bg-black p-4 font-mono text-sm"
    >
      <div className="space-y-1">
        {error ? (
          <div className="text-red-400">{error}</div>
        ) : logs.map((log: LogLine, index: number) => (
          <div 
            key={`${log.timestamp}-${index}`}
            className={
              log.type === 'error' ? 'text-red-400' :
              log.type === 'success' ? 'text-green-400' :
              'text-gray-300'
            }
          >
            <span className="text-gray-500">[{log.timestamp}]</span>{' '}
            {log.message}
          </div>
        ))}
        {logs.length === 0 && (
          <div className="text-gray-500">Waiting for logs...</div>
        )}
      </div>
    </ScrollArea>
  );
}
