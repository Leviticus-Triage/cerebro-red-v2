import { useMemo } from 'react';
import { ExperimentStatus } from '@/types/api';

interface ProgressData {
  currentIteration: number;
  totalIterations: number;
  backendStatus: ExperimentStatus;
}

interface ProgressResult {
  progressPercent: number;
  displayStatus: ExperimentStatus;
  isComplete: boolean;
  isRunning: boolean;
}

/**
 * Centralized hook for experiment progress calculation
 * 
 * Rules:
 * - Progress = (current / total) * 100, capped at 100%
 * - Status = 'completed' ONLY if current >= total OR backend says 'completed'
 * - Status = 'running' if current < total AND backend is 'running'
 */
export const useExperimentProgress = ({
  currentIteration,
  totalIterations,
  backendStatus,
}: ProgressData): ProgressResult => {
  return useMemo(() => {
    // Calculate progress (0-100%)
    const progressPercent = totalIterations > 0
      ? Math.min((currentIteration / totalIterations) * 100, 100)
      : 0;

    // Determine display status - check terminal states FIRST before iteration-based completion
    let displayStatus: ExperimentStatus;
    
    // Terminal states (FAILED, PAUSED) override iteration-based completion
    const isFailed = backendStatus === ExperimentStatus.FAILED;
    const isPaused = backendStatus === ExperimentStatus.PAUSED;
    const isCompleted = backendStatus === ExperimentStatus.COMPLETED;
    const iterationsDone = currentIteration >= totalIterations && totalIterations > 0;
    
    if (isFailed) {
      displayStatus = ExperimentStatus.FAILED;
    } else if (isPaused) {
      displayStatus = ExperimentStatus.PAUSED;
    } else if (iterationsDone && !isFailed) {
      // Only set COMPLETED if iterations are done AND backend status is not FAILED
      displayStatus = ExperimentStatus.COMPLETED;
    } else if (isCompleted) {
      displayStatus = ExperimentStatus.COMPLETED;
    } else if (currentIteration > 0 && currentIteration < totalIterations) {
      displayStatus = ExperimentStatus.RUNNING;
    } else {
      // Default to backend status
      displayStatus = backendStatus;
    }

    // Determine if experiment is complete (only when status is COMPLETED, not FAILED)
    const isComplete = 
      (iterationsDone && !isFailed) ||
      isCompleted;

    const isRunning = displayStatus === ExperimentStatus.RUNNING;

    // Debug logging
    console.log('[useExperimentProgress]', {
      currentIteration,
      totalIterations,
      backendStatus,
      progressPercent,
      displayStatus,
      isComplete,
    });

    return {
      progressPercent,
      displayStatus,
      isComplete,
      isRunning,
    };
  }, [currentIteration, totalIterations, backendStatus]);
};
