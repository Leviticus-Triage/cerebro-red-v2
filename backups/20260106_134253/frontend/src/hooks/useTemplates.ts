/**
 * React Query hooks for experiment templates.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, DEFAULT_PAGE_SIZE } from '@/lib/api/client';
import type { ExperimentTemplateCreate, ExperimentTemplateUpdate } from '@/types/api';

export function useTemplates(
  page = 1, 
  pageSize = DEFAULT_PAGE_SIZE,
  filters?: { is_public?: boolean; created_by?: string; tags?: string }
) {
  return useQuery({
    queryKey: ['templates', page, pageSize, filters],
    queryFn: () => apiClient.getTemplates(page, pageSize, filters),
    staleTime: 15 * 60 * 1000, // 15 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
}

export function useTemplate(templateId: string | undefined) {
  return useQuery({
    queryKey: ['template', templateId],
    queryFn: () => apiClient.getTemplate(templateId!),
    enabled: !!templateId,
  });
}

export function useCreateTemplate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (template: ExperimentTemplateCreate) => apiClient.createTemplate(template),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });
}

export function useUpdateTemplate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ templateId, update }: { templateId: string; update: ExperimentTemplateUpdate }) =>
      apiClient.updateTemplate(templateId, update),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      queryClient.invalidateQueries({ queryKey: ['template', variables.templateId] });
    },
  });
}

export function useDeleteTemplate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (templateId: string) => apiClient.deleteTemplate(templateId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });
}

export function useUseTemplate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (templateId: string) => apiClient.useTemplate(templateId),
    onSuccess: (data) => {
      // Invalidate to refresh usage_count
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      queryClient.invalidateQueries({ queryKey: ['template', data.template_id] });
    },
  });
}
