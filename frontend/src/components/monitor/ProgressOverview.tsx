/**
 * ProgressOverview - Shows experiment progress and key metrics
 *
 * Displays progress bar, elapsed time, current iteration, and summary stats.
 */

import React from 'react';
import type { ExperimentStatus } from '@/types/api';

interface ProgressOverviewProps {
  experimentId: string;
  experimentName: string;
  status: ExperimentStatus;
  currentIteration: number;
  totalIterations: number;
  progressPercent: number;
  elapsedSeconds: number;
  successfulIterations?: number;
  vulnerabilitiesFound?: number;
  isConnected: boolean;
  failureReason?: string;
  successThreshold?: number;
}

const statusConfig: Record<string, { label: string; color: string; bgColor: string }> = {
  pending: { label: 'Pending', color: 'text-slate-400', bgColor: 'bg-slate-700' },
  running: { label: 'Running', color: 'text-cyan-400', bgColor: 'bg-cyan-600' },
  paused: { label: 'Paused', color: 'text-amber-400', bgColor: 'bg-amber-600' },
  completed: { label: 'Completed', color: 'text-green-400', bgColor: 'bg-green-600' },
  failed: { label: 'Failed', color: 'text-red-400', bgColor: 'bg-red-600' },
};

const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  }
  if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  }
  return `${secs}s`;
};

export const ProgressOverview: React.FC<ProgressOverviewProps> = ({
  experimentId,
  experimentName,
  status,
  currentIteration,
  totalIterations,
  progressPercent,
  elapsedSeconds,
  successfulIterations = 0,
  vulnerabilitiesFound = 0,
  isConnected,
  failureReason,
  successThreshold = 7.0,
}) => {
  const config = statusConfig[status] || statusConfig.pending;

  // Determine failure explanation
  const getFailureExplanation = () => {
    if (status !== 'failed') return null;

    if (failureReason) return failureReason;

    // IMPORTANT: Check if there were successful iterations - if yes, don't show failure message
    if (successfulIterations > 0) {
      return `Experiment abgeschlossen. ${successfulIterations} erfolgreiche Jailbreak(s) gefunden.`;
    }

    // Infer reason from data
    if (successfulIterations === 0 && currentIteration > 0) {
      return `Kein Jailbreak erfolgreich. Alle ${currentIteration} Iterationen hatten einen Score unter ${successThreshold} (Threshold). Das Target-Modell hat allen Angriffen widerstanden. Das ist ein POSITIVES Ergebnis für die Sicherheit!`;
    }

    return 'Experiment wurde ohne erfolgreichen Jailbreak beendet.';
  };
  const estimatedRemaining =
    totalIterations > 0 && currentIteration > 0
      ? (elapsedSeconds / currentIteration) * (totalIterations - currentIteration)
      : 0;

  return (
    <div className="bg-slate-950 rounded-lg border border-slate-800 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div>
            <h2 className="text-lg font-bold text-slate-200">{experimentName}</h2>
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span className="font-mono">{experimentId.slice(0, 8)}...</span>
              <span className={`px-2 py-0.5 rounded ${config.bgColor} ${config.color}`}>
                {config.label}
              </span>
            </div>
          </div>
        </div>

        {/* Connection Status */}
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}
          />
          <span className={`text-xs ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
            {isConnected ? 'Live' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-sm mb-1">
          <span className="text-slate-400">Progress</span>
          <span className="text-slate-300 font-mono">
            {Math.min(progressPercent, 100).toFixed(1)}%
          </span>
        </div>
        <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${
              status === 'running'
                ? 'bg-gradient-to-r from-cyan-600 to-cyan-400'
                : status === 'completed'
                  ? 'bg-gradient-to-r from-green-600 to-green-400'
                  : status === 'failed'
                    ? 'bg-gradient-to-r from-red-600 to-red-400'
                    : 'bg-slate-600'
            }`}
            style={{ width: `${Math.min(progressPercent, 100)}%` }}
          />
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Iterations */}
        <div className="bg-slate-900/50 rounded-lg p-3">
          <div className="text-xs text-slate-500 mb-1">Iterations</div>
          <div className="text-xl font-bold text-slate-200">
            {Math.min(currentIteration, totalIterations)} / {totalIterations}
          </div>
        </div>

        {/* Elapsed Time */}
        <div className="bg-slate-900/50 rounded-lg p-3">
          <div className="text-xs text-slate-500 mb-1">Elapsed</div>
          <div className="text-xl font-bold text-slate-200">{formatDuration(elapsedSeconds)}</div>
        </div>

        {/* Estimated Remaining */}
        <div className="bg-slate-900/50 rounded-lg p-3">
          <div className="text-xs text-slate-500 mb-1">Est. Remaining</div>
          <div className="text-xl font-bold text-slate-200">
            {status === 'running' && estimatedRemaining > 0
              ? formatDuration(estimatedRemaining)
              : '—'}
          </div>
        </div>

        {/* Vulnerabilities */}
        <div
          className={`rounded-lg p-3 ${
            vulnerabilitiesFound > 0 ? 'bg-red-950/50' : 'bg-slate-900/50'
          }`}
        >
          <div className="text-xs text-slate-500 mb-1">Vulnerabilities</div>
          <div
            className={`text-xl font-bold ${
              vulnerabilitiesFound > 0 ? 'text-red-400' : 'text-green-400'
            }`}
          >
            {vulnerabilitiesFound}
          </div>
        </div>
      </div>

      {/* Success Rate (if applicable) */}
      {successfulIterations > 0 && (
        <div className="mt-4 p-3 bg-red-950/30 border border-red-800 rounded-lg">
          <div className="flex items-center gap-2 text-red-400">
            <span className="font-medium">
              {successfulIterations} successful jailbreak{successfulIterations > 1 ? 's' : ''}{' '}
              detected
            </span>
            <span className="text-xs text-red-500">
              ({((successfulIterations / Math.max(currentIteration, 1)) * 100).toFixed(1)}% success
              rate)
            </span>
          </div>
        </div>
      )}

      {/* Failed Status Explanation */}
      {status === 'failed' && (
        <div className="mt-4 p-3 bg-amber-950/30 border border-amber-700 rounded-lg">
          <div className="flex items-start gap-2 text-amber-400">
            <div>
              <span className="font-medium block mb-1">Experiment Status: Failed</span>
              <span className="text-sm text-amber-300/80">{getFailureExplanation()}</span>
            </div>
          </div>
        </div>
      )}

      {/* Completed with no vulnerabilities - positive result */}
      {status === 'completed' && vulnerabilitiesFound === 0 && successfulIterations === 0 && (
        <div className="mt-4 p-3 bg-green-950/30 border border-green-700 rounded-lg">
          <div className="flex items-center gap-2 text-green-400">
            <span className="font-medium">
              Target-Modell hat allen Angriffen widerstanden! Keine Schwachstellen gefunden.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgressOverview;
