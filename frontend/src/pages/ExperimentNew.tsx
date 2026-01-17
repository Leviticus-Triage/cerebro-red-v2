/**
 * New experiment creation page.
 */

import { useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ExperimentForm } from '@/components/experiments/ExperimentForm';
import { useCreateExperiment, useStartScan } from '@/hooks/useExperiments';
import type { ExperimentConfig, ExperimentTemplate } from '@/types/api';

export function ExperimentNew() {
  const navigate = useNavigate();
  const location = useLocation();
  const createExperiment = useCreateExperiment();
  const startScan = useStartScan();

  // Check if template was passed via navigation state
  const template = location.state?.template as ExperimentTemplate | undefined;
  const initialConfig = template?.config;

  const handleSubmit = async (data: ExperimentConfig) => {
    try {
      const result = await createExperiment.mutateAsync(data);
      // apiClient.createExperiment() now returns ExperimentResponse directly (unwrapped)
      // So result is already the ExperimentResponse object
      const experiment = result;
      const experimentId = experiment?.experiment_id;

      if (!experimentId) {
        console.error('Invalid response structure:', result);
        throw new Error('Experiment ID not found in response');
      }

      // Update data with experiment_id for scan
      const scanData = { ...data, experiment_id: experimentId };

      // Automatically start the scan
      await startScan.mutateAsync(scanData);
      navigate(`/experiments/${experimentId}`);
    } catch (error: unknown) {
      console.error('Failed to create experiment:', error);
      const errorMessage =
        (error as { response?: { data?: { detail?: string } }; message?: string })?.response?.data
          ?.detail ||
        (error as { message?: string })?.message ||
        'Unknown error';
      alert(`Failed to create experiment: ${errorMessage}`);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">New Experiment</h1>
        <p className="text-muted-foreground">Configure a new PAIR experiment</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Experiment Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <ExperimentForm
            onSubmit={handleSubmit}
            isLoading={createExperiment.isPending || startScan.isPending}
            initialConfig={initialConfig}
          />
        </CardContent>
      </Card>
    </div>
  );
}
