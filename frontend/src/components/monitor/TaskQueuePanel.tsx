/**
 * TaskQueuePanel - Shows task queue and completed tasks
 *
 * Displays pending, running, and completed tasks with progress indicators.
 */

import React from 'react';
import type { TaskQueueItem } from '@/types/api';

interface TaskQueuePanelProps {
  tasks: TaskQueueItem[];
}

const statusConfig: Record<string, { color: string; bgColor: string }> = {
  queued: { color: 'text-slate-400', bgColor: 'bg-slate-800' },
  running: { color: 'text-cyan-400', bgColor: 'bg-cyan-950/50' },
  completed: { color: 'text-green-400', bgColor: 'bg-green-950/30' },
  failed: { color: 'text-red-400', bgColor: 'bg-red-950/30' },
};

export const TaskQueuePanel: React.FC<TaskQueuePanelProps> = ({ tasks }) => {
  const queuedTasks = tasks.filter((t) => t.status === 'queued');
  const runningTasks = tasks.filter((t) => t.status === 'running');
  const completedTasks = tasks.filter((t) => t.status === 'completed' || t.status === 'failed');

  const formatTime = (timestamp?: string) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('de-DE', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const renderTask = (task: TaskQueueItem) => {
    const config = statusConfig[task.status];

    // Check if task has dependencies (Phase 6)
    const hasDependencies = task.dependencies && task.dependencies.length > 0;

    return (
      <div
        key={task.id}
        className={`flex items-center gap-3 px-3 py-2 rounded-lg ${config.bgColor} transition-all`}
      >
        <div className="flex-1 min-w-0">
          <div className={`font-medium ${config.color} truncate`}>{task.name}</div>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            {task.iteration !== undefined && <span>Iteration {task.iteration}</span>}
            {task.queuePosition !== undefined && task.status === 'queued' && (
              <span className="px-1.5 py-0.5 bg-blue-900/30 text-blue-400 rounded text-[10px]">
                #{task.queuePosition}
              </span>
            )}
            {task.strategy && (
              <span className="px-1.5 py-0.5 bg-slate-700 rounded text-slate-400">
                {task.strategy}
              </span>
            )}
            {hasDependencies && (
              <span className="px-1.5 py-0.5 bg-amber-900/30 text-amber-400 rounded text-[10px]">
                {task.dependencies!.length} dep{task.dependencies!.length > 1 ? 's' : ''}
              </span>
            )}
            {task.startedAt && <span>Started: {formatTime(task.startedAt)}</span>}
            {task.completedAt && <span>Done: {formatTime(task.completedAt)}</span>}
          </div>
        </div>
        {task.status === 'running' && (
          <div className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 rounded-lg border border-slate-800 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-900/80 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <span className="text-lg"></span>
          <h3 className="font-semibold text-slate-200">Task Queue</h3>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="px-2 py-0.5 bg-slate-800 text-slate-400 rounded-full">
            {queuedTasks.length} queued
          </span>
          <span className="px-2 py-0.5 bg-cyan-900/50 text-cyan-400 rounded-full">
            {runningTasks.length} running
          </span>
          <span className="px-2 py-0.5 bg-green-900/30 text-green-400 rounded-full">
            {completedTasks.length} done
          </span>
        </div>
      </div>

      {/* Task Lists */}
      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {/* Running Tasks */}
        {runningTasks.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">
              Running
            </h4>
            {runningTasks.map(renderTask)}
          </div>
        )}

        {/* Queued Tasks */}
        {queuedTasks.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Queued ({queuedTasks.length})
            </h4>
            {queuedTasks.map(renderTask)}
          </div>
        )}

        {/* Completed Tasks (reversed to show most recent first) */}
        {completedTasks.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-green-400 uppercase tracking-wider">
              Completed ({completedTasks.length})
            </h4>
            {completedTasks.slice().reverse().slice(0, 10).map(renderTask)}
            {completedTasks.length > 10 && (
              <div className="text-xs text-slate-500 text-center py-1">
                ... and {completedTasks.length - 10} more
              </div>
            )}
          </div>
        )}

        {/* Empty State */}
        {tasks.length === 0 && (
          <div className="flex items-center justify-center h-full text-slate-500">
            <span>No tasks yet</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskQueuePanel;
