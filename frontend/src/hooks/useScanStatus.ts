/**
 * React Query hooks for scan status.
 */

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';

export function useScanStatus(experimentId: string | undefined, enabled = true) {
  return useQuery({
    queryKey: ['scan-status', experimentId],
    queryFn: () => apiClient.getScanStatus(experimentId!),
    enabled: !!experimentId && enabled,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.status === 'running') {
        return 2000; // Poll every 2 seconds when running
      }
      return false; // Don't poll when not running
    },
  });
}

