/**
 * Experiment details page with real-time progress and results.
 */

import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AttackProgress } from '@/components/experiments/AttackProgress';
import { VulnerabilityHeatmap } from '@/components/vulnerabilities/VulnerabilityHeatmap';
import { JudgeScoreChart } from '@/components/charts/JudgeScoreChart';
import { StrategyDistributionChart } from '@/components/charts/StrategyDistributionChart';
import { MutationTimeline } from '@/components/charts/MutationTimeline';
import { JudgeScoreCard } from '@/components/charts/JudgeScoreCard';
import { StatusBadge } from '@/components/common/StatusBadge';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { apiClient } from '@/lib/api/client';
import {
  useExperiment,
  useExperimentStatistics,
  usePauseScan,
  useResumeScan,
  useCancelScan,
  useRepeatExperiment,
  useDeleteExperiment,
} from '@/hooks/useExperiments';
import { exportExperimentResults } from '@/lib/export';
import { Download, Pause, Play, ChevronDown, Eye, RotateCw, Trash2, Square } from 'lucide-react';
import { toast } from '@/lib/toast';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { formatDate } from '@/lib/utils';
import { useExperimentProgress } from '@/hooks/useExperimentProgress';
import { ExperimentStatus } from '@/types/api';
import type { AttackIteration } from '@/types/api';

export function ExperimentDetails() {
  const { experimentId } = useParams<{ experimentId: string }>();
  const navigate = useNavigate();
  const [exportMenuOpen, setExportMenuOpen] = useState(false);
  const exportMenuRef = useRef<HTMLDivElement>(null);
  const isClosingRef = useRef(false);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (exportMenuRef.current && !exportMenuRef.current.contains(event.target as Node)) {
        if (!isClosingRef.current) {
          isClosingRef.current = true;
          setExportMenuOpen(false);
          // Reset flag after a short delay
          setTimeout(() => {
            isClosingRef.current = false;
          }, 100);
        }
      }
    };

    if (exportMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [exportMenuOpen]);

  const { data: experiment, isLoading: experimentLoading } = useExperiment(experimentId);

  // Debug-Logging
  useEffect(() => {
    if (experiment) {
      console.log('[ExperimentDetails] Experiment loaded:', {
        id: experiment.experiment_id,
        status: experiment.status,
        max_iterations: experiment.max_iterations,
        initial_prompts: experiment.initial_prompts?.length,
      });
    }
  }, [experiment]);

  // Close dropdown when experiment status changes (e.g., when starting)
  const prevStatusRef = useRef<string | undefined>(experiment?.status);

  useEffect(() => {
    if (experiment?.status && prevStatusRef.current !== experiment.status) {
      // Status changed - close dropdown if it was open
      if (exportMenuOpen) {
        setExportMenuOpen(false);
      }
      prevStatusRef.current = experiment.status;
    }
  }, [experiment?.status, exportMenuOpen]);
  const { data: statistics } = useExperimentStatistics(experimentId);
  const { data: results } = useQuery({
    queryKey: ['experiment-results', experimentId],
    queryFn: () => apiClient.getExperimentResults(experimentId!),
    enabled: !!experimentId,
  });

  // Use centralized progress hook for Overview display
  const { progressPercent, displayStatus } = useExperimentProgress({
    currentIteration: statistics?.total_iterations || 0, // Use total_iterations as current if available
    totalIterations: experiment?.max_iterations || 0,
    backendStatus: (experiment?.status as ExperimentStatus) || 'pending',
  });

  const pauseScan = usePauseScan();
  const resumeScan = useResumeScan();
  const cancelScan = useCancelScan();
  const repeatExperiment = useRepeatExperiment();
  const deleteExperiment = useDeleteExperiment();

  if (experimentLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!experiment) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">Experiment not found</p>
      </div>
    );
  }

  const exp = experiment;
  const isRunning = exp.status === 'running';
  const isPaused = exp.status === 'paused';
  const canControl = isRunning || isPaused; // Can pause/resume/cancel when running or paused

  const handlePause = () => {
    if (experimentId && isRunning) {
      pauseScan.mutate(experimentId, {
        onSuccess: () => toast.success('Experiment paused'),
        onError: (error: Error) => toast.error(`Failed to pause: ${error.message}`),
      });
    }
  };

  const handleResume = () => {
    if (experimentId && isPaused) {
      resumeScan.mutate(experimentId, {
        onSuccess: () => toast.success('Experiment resumed'),
        onError: (error: Error) => toast.error(`Failed to resume: ${error.message}`),
      });
    }
  };

  const handleCancel = () => {
    if (experimentId && canControl) {
      if (confirm('Are you sure you want to cancel this experiment?')) {
        cancelScan.mutate(experimentId, {
          onSuccess: () => toast.success('Experiment cancelled'),
          onError: (error: Error) => toast.error(`Failed to cancel: ${error.message}`),
        });
      }
    }
  };

  const handleRepeat = () => {
    if (experimentId) {
      repeatExperiment.mutate(experimentId, {
        onSuccess: (newExperiment) => {
          toast.success(`Experiment "${newExperiment.name}" created`);
          navigate(`/experiments/${newExperiment.experiment_id}`);
        },
        onError: (error: Error) => toast.error(`Failed to repeat: ${error.message}`),
      });
    }
  };

  const handleDelete = () => {
    if (experimentId) {
      if (
        confirm('Are you sure you want to delete this experiment? This action cannot be undone.')
      ) {
        deleteExperiment.mutate(experimentId, {
          onSuccess: () => {
            toast.success('Experiment deleted');
            navigate('/experiments');
          },
          onError: (error: Error) => toast.error(`Failed to delete: ${error.message}`),
        });
      }
    }
  };

  const handleExport = (format: 'json' | 'csv' | 'pdf') => {
    if (experimentId) {
      exportExperimentResults(experimentId, format).catch(console.error);
      setExportMenuOpen(false); // Close menu after export
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{exp.name}</h1>
          <p className="text-muted-foreground">{exp.description}</p>
        </div>
        <div className="flex items-center gap-2">
          <StatusBadge status={exp.status} />
          {/* Live Monitor Button */}
          <Button
            variant="default"
            size="sm"
            onClick={() => navigate(`/experiments/${experimentId}/monitor`)}
            className="bg-cyan-600 hover:bg-cyan-500"
          >
            <Eye className="mr-2 h-4 w-4" />
            Live Monitor
          </Button>

          {/* Repeat Button */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleRepeat}
            disabled={repeatExperiment.isPending}
          >
            <RotateCw
              className={`mr-2 h-4 w-4 ${repeatExperiment.isPending ? 'animate-spin' : ''}`}
            />
            Repeat
          </Button>

          {/* Pause Button - only enabled when running */}
          <Button
            variant="outline"
            size="sm"
            onClick={handlePause}
            disabled={!isRunning || pauseScan.isPending}
          >
            <Pause className="mr-2 h-4 w-4" />
            Pause
          </Button>

          {/* Resume Button - only enabled when paused */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleResume}
            disabled={!isPaused || resumeScan.isPending}
          >
            <Play className="mr-2 h-4 w-4" />
            Resume
          </Button>

          {/* Cancel/Stop Button - enabled when running or paused */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleCancel}
            disabled={!canControl || cancelScan.isPending}
          >
            <Square className="mr-2 h-4 w-4" />
            Stop
          </Button>

          {/* Delete Button - always visible but disabled when running/paused */}
          <Button
            variant="destructive"
            size="sm"
            onClick={handleDelete}
            disabled={canControl || deleteExperiment.isPending}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </Button>

          <div className="relative" ref={exportMenuRef}>
            <Button variant="outline" size="sm" onClick={() => setExportMenuOpen(!exportMenuOpen)}>
              <Download className="mr-2 h-4 w-4" />
              Export
              <ChevronDown
                className={`ml-2 h-4 w-4 transition-transform ${exportMenuOpen ? 'rotate-180' : ''}`}
              />
            </Button>
            {exportMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-popover border border-border z-50">
                <div className="py-1">
                  <button
                    onClick={() => handleExport('json')}
                    className="w-full text-left px-4 py-2 text-sm hover:bg-accent hover:text-accent-foreground transition-colors"
                  >
                    Export as JSON
                  </button>
                  <button
                    onClick={() => handleExport('csv')}
                    className="w-full text-left px-4 py-2 text-sm hover:bg-accent hover:text-accent-foreground transition-colors"
                  >
                    Export as CSV
                  </button>
                  <button
                    onClick={() => handleExport('pdf')}
                    className="w-full text-left px-4 py-2 text-sm hover:bg-accent hover:text-accent-foreground transition-colors"
                  >
                    Export as PDF
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Always show AttackProgress if experiment exists (not just when running) */}
      {experimentId && <AttackProgress experimentId={experimentId} />}

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="iterations">Iterations</TabsTrigger>
          <TabsTrigger value="vulnerabilities">Vulnerabilities</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Target Model:</span>
                  <span>{exp.target_model_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Max Iterations:</span>
                  <span>{exp.max_iterations}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Success Threshold:</span>
                  <span>{exp.success_threshold}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Created:</span>
                  <span>{formatDate(exp.created_at)}</span>
                </div>
              </CardContent>
            </Card>

            {statistics && (
              <Card>
                <CardHeader>
                  <CardTitle>Statistics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Total Iterations:</span>
                    <span>{statistics.total_iterations || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Success Rate:</span>
                    <span>{((statistics?.success_rate || 0) * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Vulnerabilities:</span>
                    <span>{statistics?.vulnerabilities_found || 0}</span>
                  </div>
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader>
                <CardTitle>Progress & Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Progress:</span>
                  <span>
                    {statistics?.total_iterations || 0}/{experiment?.max_iterations || 0} (
                    {progressPercent.toFixed(1)}%)
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <StatusBadge status={displayStatus} />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="iterations">
          {results?.iterations && results.iterations.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>Iterations</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>#</TableHead>
                      <TableHead>Strategy</TableHead>
                      <TableHead>Score</TableHead>
                      <TableHead>Success</TableHead>
                      <TableHead>Timestamp</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {results.iterations.map((iteration: AttackIteration) => (
                      <TableRow key={iteration.iteration_id}>
                        <TableCell>{iteration.iteration_number}</TableCell>
                        <TableCell>{iteration.strategy_used}</TableCell>
                        <TableCell>{iteration.judge_score.toFixed(2)}</TableCell>
                        <TableCell>
                          {iteration.success ? (
                            <span className="text-green-500"></span>
                          ) : (
                            <span className="text-red-500"></span>
                          )}
                        </TableCell>
                        <TableCell>{formatDate(iteration.timestamp)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          ) : (
            <p className="text-sm text-muted-foreground">No iterations yet</p>
          )}
        </TabsContent>

        <TabsContent value="vulnerabilities">
          {results?.vulnerabilities && results.vulnerabilities.length > 0 ? (
            <VulnerabilityHeatmap vulnerabilities={results.vulnerabilities} />
          ) : (
            <p className="text-sm text-muted-foreground">No vulnerabilities found</p>
          )}
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          {results?.iterations && results.iterations.length > 0 && (
            <>
              <JudgeScoreCard iterations={results.iterations} />
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {statistics?.strategy_distribution && (
                  <StrategyDistributionChart data={statistics.strategy_distribution} />
                )}
                <JudgeScoreChart iterations={results.iterations} />
              </div>
              <MutationTimeline iterations={results.iterations} />
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
