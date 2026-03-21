import { QueryClient } from '@tanstack/react-query';
import { apiClient, DEFAULT_PAGE_SIZE } from '@/lib/api/client';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 60 * 1000, retry: 1 },
  },
});

export async function prefetchNextExperimentsPage(page: number, pageSize: number): Promise<void> {
  await queryClient.prefetchQuery({
    queryKey: ['experiments', page + 1, pageSize],
    queryFn: () => apiClient.getExperiments(page + 1, pageSize),
  });
}

export { DEFAULT_PAGE_SIZE };
