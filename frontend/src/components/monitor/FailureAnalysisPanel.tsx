/**
 * FailureAnalysisPanel - Displays detailed failure analysis for failed experiments
 *
 * Shows comprehensive breakdown of why an experiment failed, including:
 * - Failure reason classification
 * - Best result achieved
 * - Strategy performance analysis
 * - Score progression chart
 * - Actionable recommendations
 */

import React from 'react';
import { X, AlertCircle, TrendingUp, Target, Lightbulb } from 'lucide-react';
import { FailureAnalysis } from '@/types/api';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface FailureAnalysisPanelProps {
  analysis: FailureAnalysis;
  onClose: () => void;
}

const failureReasonLabels: Record<string, { label: string; description: string; color: string }> = {
  max_iterations_reached: {
    label: 'Max Iterations Reached',
    description: 'Experiment reached maximum iteration limit without achieving success threshold',
    color: 'text-amber-400',
  },
  consistent_low_scores: {
    label: 'Consistent Low Scores',
    description: 'All attack attempts scored below half of the success threshold',
    color: 'text-red-400',
  },
  all_strategies_exhausted: {
    label: 'All Strategies Exhausted',
    description: 'All configured attack strategies were tried without success',
    color: 'text-orange-400',
  },
  target_model_robust: {
    label: 'Target Model Robust',
    description: 'Target model successfully defended against all attacks',
    color: 'text-green-400',
  },
  no_iterations_executed: {
    label: 'No Iterations Executed',
    description: 'Experiment failed before any iterations could be executed',
    color: 'text-gray-400',
  },
  unknown: {
    label: 'Unknown Reason',
    description: 'Unable to determine specific failure reason',
    color: 'text-slate-400',
  },
};

export const FailureAnalysisPanel: React.FC<FailureAnalysisPanelProps> = ({
  analysis,
  onClose,
}) => {
  const reasonInfo = failureReasonLabels[analysis.failure_reason] || failureReasonLabels.unknown;

  // Prepare chart data
  const chartData = analysis.iteration_breakdown.map((item) => ({
    iteration: item.iteration,
    score: item.score,
    threshold: analysis.success_threshold,
    strategy: item.strategy,
  }));

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-200">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-red-950/30 border-b border-red-900/50">
        <div className="flex items-center gap-3">
          <AlertCircle className="w-6 h-6 text-red-400" />
          <div>
            <h2 className="text-xl font-bold text-red-400">Experiment Failed</h2>
            <p className="text-sm text-slate-400 mt-0.5">{reasonInfo.description}</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5 text-slate-400" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Failure Reason Badge */}
        <div
          className={`px-4 py-3 rounded-lg bg-slate-900 border border-slate-700 ${reasonInfo.color}`}
        >
          <div className="font-semibold text-lg mb-1">{reasonInfo.label}</div>
          <div className="text-sm text-slate-400">{reasonInfo.description}</div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
            <div className="text-xs text-slate-400 mb-1">Iterations Executed</div>
            <div className="text-2xl font-bold text-slate-200">
              {analysis.iterations_executed} / {analysis.max_iterations}
            </div>
          </div>

          <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
            <div className="text-xs text-slate-400 mb-1 flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              Best Score
            </div>
            <div className="text-2xl font-bold text-amber-400">
              {analysis.best_score.toFixed(2)}
            </div>
            <div className="text-xs text-slate-500 mt-1">Iteration {analysis.best_iteration}</div>
          </div>

          <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
            <div className="text-xs text-slate-400 mb-1 flex items-center gap-1">
              <Target className="w-3 h-3" />
              Threshold Gap
            </div>
            <div className="text-2xl font-bold text-red-400">
              {analysis.threshold_gap.toFixed(2)}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Target: {analysis.success_threshold.toFixed(1)}
            </div>
          </div>

          <div className="bg-slate-900 rounded-lg p-4 border border-slate-800">
            <div className="text-xs text-slate-400 mb-1">Best Strategy</div>
            <div className="text-lg font-semibold text-cyan-400 truncate">
              {analysis.best_strategy}
            </div>
          </div>
        </div>

        {/* Strategy Performance Table */}
        {Object.keys(analysis.strategy_performance).length > 0 && (
          <div className="bg-slate-900 rounded-lg border border-slate-800 overflow-hidden">
            <div className="px-4 py-3 bg-slate-800/50 border-b border-slate-700">
              <h3 className="font-semibold text-slate-200">Strategy Performance</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-800/30">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-semibold text-slate-400 uppercase">
                      Strategy
                    </th>
                    <th className="px-4 py-2 text-right text-xs font-semibold text-slate-400 uppercase">
                      Attempts
                    </th>
                    <th className="px-4 py-2 text-right text-xs font-semibold text-slate-400 uppercase">
                      Avg Score
                    </th>
                    <th className="px-4 py-2 text-right text-xs font-semibold text-slate-400 uppercase">
                      Success Rate
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {Object.entries(analysis.strategy_performance)
                    .sort((a, b) => b[1].avg_score - a[1].avg_score)
                    .map(([strategy, perf]) => (
                      <tr key={strategy} className="hover:bg-slate-800/30">
                        <td className="px-4 py-2 text-slate-300 font-mono text-sm">{strategy}</td>
                        <td className="px-4 py-2 text-right text-slate-400">{perf.attempts}</td>
                        <td className="px-4 py-2 text-right">
                          <span
                            className={`font-semibold ${
                              perf.avg_score >= analysis.success_threshold * 0.7
                                ? 'text-amber-400'
                                : perf.avg_score >= analysis.success_threshold * 0.5
                                  ? 'text-orange-400'
                                  : 'text-red-400'
                            }`}
                          >
                            {perf.avg_score.toFixed(2)}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-right">
                          <span
                            className={`font-semibold ${
                              perf.success_rate > 0.5
                                ? 'text-green-400'
                                : perf.success_rate > 0
                                  ? 'text-yellow-400'
                                  : 'text-red-400'
                            }`}
                          >
                            {(perf.success_rate * 100).toFixed(1)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Score Progression Chart */}
        {analysis.iteration_breakdown.length > 0 && (
          <div className="bg-slate-900 rounded-lg border border-slate-800 p-4">
            <h3 className="font-semibold text-slate-200 mb-4">Score Progression</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis
                  dataKey="iteration"
                  stroke="#94a3b8"
                  label={{
                    value: 'Iteration',
                    position: 'insideBottom',
                    offset: -5,
                    fill: '#94a3b8',
                  }}
                />
                <YAxis
                  stroke="#94a3b8"
                  domain={[0, 10]}
                  label={{ value: 'Score', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '6px',
                  }}
                  labelStyle={{ color: '#cbd5e1' }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6', r: 4 }}
                  name="Judge Score"
                />
                <Line
                  type="monotone"
                  dataKey="threshold"
                  stroke="#ef4444"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Success Threshold"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Recommendations */}
        {analysis.recommendations.length > 0 && (
          <div className="bg-slate-900 rounded-lg border border-slate-800 p-4">
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb className="w-5 h-5 text-amber-400" />
              <h3 className="font-semibold text-slate-200">Recommendations</h3>
            </div>
            <ul className="space-y-2">
              {analysis.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start gap-3 text-slate-300">
                  <span className="text-amber-400 mt-1">•</span>
                  <span className="flex-1">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default FailureAnalysisPanel;
