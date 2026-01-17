/**
 * Real-time attack progress component with WebSocket integration and API polling.
 */

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { wsClient } from '@/lib/websocket/client';
import { apiClient } from '@/lib/api/client';
import { useExperimentProgress } from '@/hooks/useExperimentProgress';
import { ExperimentStatus } from '@/types/api';
import type { WSMessage } from '@/types/api';

interface AttackProgressProps {
  experimentId: string;
}

export function AttackProgress({ experimentId }: AttackProgressProps) {
  const [statusData, setStatusData] = useState<any>(null);
  const [currentIteration, setCurrentIteration] = useState(0);
  const [totalIterations, setTotalIterations] = useState(0);
  const [currentStrategy, setCurrentStrategy] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Use centralized progress hook
  const { progressPercent, displayStatus } = useExperimentProgress({
    currentIteration: statusData?.current_iteration || 0,
    totalIterations: statusData?.total_iterations || 0,
    backendStatus: (statusData?.status as ExperimentStatus) || 'pending',
  });

  // Fetch status from API (for initial load and when WebSocket is not connected)
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const statusData = await apiClient.getScanStatus(experimentId);
        console.log('[AttackProgress] Fetched status:', statusData);

        // Robuste Validierung
        if (!statusData) {
          console.warn('[AttackProgress] Status data is null/undefined');
          setError('No status data available');
          setIsLoading(false);
          return;
        }

        // Validiere dass alle erforderlichen Felder vorhanden sind
        if (
          typeof statusData.current_iteration !== 'number' ||
          typeof statusData.total_iterations !== 'number'
        ) {
          console.error('[AttackProgress] Invalid status data structure:', statusData);
          setError('Invalid status data structure');
          setIsLoading(false);
          return;
        }

        // Store status data (hook will calculate progress and status)
        setStatusData(statusData);
        setCurrentIteration(statusData.current_iteration);
        setTotalIterations(statusData.total_iterations);
        setIsLoading(false);

        console.log('[AttackProgress] Updated state:', {
          progress: statusData.progress_percent,
          current: statusData.current_iteration,
          total: statusData.total_iterations,
          status: statusData.status,
        });
      } catch (error) {
        console.error('[AttackProgress] Failed to fetch scan status:', error);
        setError(error instanceof Error ? error.message : 'Failed to fetch status');
        setIsLoading(false);
      }
    };

    // Fetch immediately
    fetchStatus();

    // Poll every 2 seconds
    const interval = setInterval(() => {
      fetchStatus();
    }, 2000);

    return () => clearInterval(interval);
  }, [experimentId]);

  // Also listen to WebSocket for real-time updates
  useEffect(() => {
    wsClient.connect(experimentId);

    const handleProgress = (message: WSMessage) => {
      if (message.type === 'progress') {
        setCurrentIteration(message.iteration || 0);
        setTotalIterations(message.total_iterations || 0);
        setCurrentStrategy(message.current_strategy || '');
        // Update statusData (hook will calculate progress and status)
        // Guard against null by defaulting to empty object
        setStatusData((prev: any) => ({
          ...(prev ?? {}),
          current_iteration: message.iteration || 0,
          total_iterations: message.total_iterations || 0,
          status: 'running',
        }));
      }
    };

    const handleComplete = (message: WSMessage) => {
      if (message.type === 'experiment_complete') {
        // Guard against null by defaulting to empty object
        setStatusData((prev: any) => ({
          ...(prev ?? {}),
          status: 'completed',
        }));
      }
    };

    const handleConnected = (message: WSMessage) => {
      if (message.type === 'connected') {
        // No status change needed on connect
      }
    };

    wsClient.on('progress', handleProgress);
    wsClient.on('experiment_complete', handleComplete);
    wsClient.on('connected', handleConnected);

    return () => {
      wsClient.off('progress', handleProgress);
      wsClient.off('experiment_complete', handleComplete);
      wsClient.off('connected', handleConnected);
      wsClient.disconnect();
    };
  }, [experimentId]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Attack Progress</span>
          <Badge variant={displayStatus === ExperimentStatus.RUNNING ? 'default' : 'secondary'}>
            {displayStatus}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading && currentIteration === 0 ? (
          <div className="text-sm text-muted-foreground">Loading progress...</div>
        ) : error ? (
          <div className="text-sm text-destructive">Error: {error}</div>
        ) : (
          <>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>
                  Iteration {currentIteration} / {totalIterations}
                </span>
                <span>{progressPercent.toFixed(1)}%</span>
              </div>
              <Progress value={progressPercent} />
            </div>
            {currentStrategy && (
              <div className="text-sm">
                <span className="text-muted-foreground">Current Strategy:</span>{' '}
                <Badge variant="outline">{currentStrategy}</Badge>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
