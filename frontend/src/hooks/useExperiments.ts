/**
 * React Query hooks for experiments.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { apiClient, DEFAULT_PAGE_SIZE } from '@/lib/api/client';
import { prefetchNextExperimentsPage } from '@/lib/queryClient';
import type { ExperimentConfig } from '@/types/api';

export function useExperiments(page = 1, pageSize = DEFAULT_PAGE_SIZE) {
  const query = useQuery({
    queryKey: ['experiments', page, pageSize],
    queryFn: () => apiClient.getExperiments(page, pageSize),
    staleTime: 15 * 60 * 1000, // 15 minutes for lists (longer than default)
    gcTime: 30 * 60 * 1000, // 30 minutes
  });

  // Prefetch next page when current page is loaded
  useEffect(() => {
    if (query.data && query.data.items.length > 0) {
      // Only prefetch if there might be more pages
      const totalPages = Math.ceil(query.data.total / pageSize);
      if (page < totalPages) {
        prefetchNextExperimentsPage(page, pageSize).catch(() => {
          // Silently fail prefetch
        });
      }
    }
  }, [query.data, page, pageSize]);

  return query;
}

export function useExperiment(experimentId: string | undefined) {
  return useQuery({
    queryKey: ['experiment', experimentId],
    queryFn: () => apiClient.getExperiment(experimentId!),
    enabled: !!experimentId,
  });
}

export function useCreateExperiment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (config: ExperimentConfig) => apiClient.createExperiment(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experiments'] });
    },
  });
}

export function useDeleteExperiment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (experimentId: string) => apiClient.deleteExperiment(experimentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experiments'] });
    },
  });
}

export function useExperimentIterations(experimentId: string | undefined) {
  return useQuery({
    queryKey: ['experiment-iterations', experimentId],
    queryFn: () => apiClient.getExperimentIterations(experimentId!),
    enabled: !!experimentId,
  });
}

export function useExperimentStatistics(experimentId: string | undefined) {
  return useQuery({
    queryKey: ['experiment-statistics', experimentId],
    queryFn: () => apiClient.getExperimentStatistics(experimentId!),
    enabled: !!experimentId,
  });
}

export function useStartScan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (config: ExperimentConfig) => apiClient.startScan(config),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['experiments'] });
      queryClient.invalidateQueries({ queryKey: ['experiment', variables.experiment_id] });
    },
  });
}

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

export function usePauseScan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (experimentId: string) => apiClient.pauseScan(experimentId),
    onSuccess: (_, experimentId) => {
      queryClient.invalidateQueries({ queryKey: ['scan-status', experimentId] });
      queryClient.invalidateQueries({ queryKey: ['experiment', experimentId] });
    },
  });
}

export function useResumeScan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (experimentId: string) => apiClient.resumeScan(experimentId),
    onSuccess: (_, experimentId) => {
      queryClient.invalidateQueries({ queryKey: ['scan-status', experimentId] });
      queryClient.invalidateQueries({ queryKey: ['experiment', experimentId] });
    },
  });
}

export function useCancelScan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (experimentId: string) => apiClient.cancelScan(experimentId),
    onSuccess: (_, experimentId) => {
      queryClient.invalidateQueries({ queryKey: ['scan-status', experimentId] });
      queryClient.invalidateQueries({ queryKey: ['experiment', experimentId] });
    },
  });
}

export function useRepeatExperiment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (experimentId: string) => apiClient.repeatExperiment(experimentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['experiments'] });
    },
  });
}
