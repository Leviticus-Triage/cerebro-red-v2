/**
 * React Query hooks for vulnerabilities.
 */

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';

export function useVulnerabilities(filters?: {
  severity?: string;
  experiment_id?: string;
  strategy?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery({
    queryKey: ['vulnerabilities', filters],
    queryFn: () => apiClient.getVulnerabilities(filters),
  });
}

export function useVulnerability(vulnerabilityId: string | undefined) {
  return useQuery({
    queryKey: ['vulnerability', vulnerabilityId],
    queryFn: () => apiClient.getVulnerability(vulnerabilityId!),
    enabled: !!vulnerabilityId,
  });
}

export function useVulnerabilityStatistics() {
  return useQuery({
    queryKey: ['vulnerability-statistics'],
    queryFn: () => apiClient.getVulnerabilityStatistics(),
  });
}

