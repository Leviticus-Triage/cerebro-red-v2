import { apiClient } from '@/lib/api/client';

export async function exportExperimentResults(
  experimentId: string,
  format: 'json' | 'csv' | 'pdf'
): Promise<void> {
  const data = await apiClient.getExperimentResults(experimentId);
  const blob =
    format === 'json'
      ? new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      : new Blob([String(data)], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `experiment-${experimentId}.${format === 'pdf' ? 'txt' : format}`;
  a.click();
  URL.revokeObjectURL(url);
}
