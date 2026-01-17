/**
 * IterationResultsPanel - Shows detailed results for each iteration
 *
 * Displays prompts, responses, scores, and success status for each iteration.
 */

import React, { useState } from 'react';
import type { IterationResult } from '@/types/api';
import { LatencyBreakdownChart, TokenPieChart, JudgeScoresRadar } from './charts';

interface IterationResultsPanelProps {
  iterations: IterationResult[];
  successThreshold?: number;
}

const getScoreColor = (score: number, threshold: number) => {
  if (score >= threshold) return 'text-red-400 bg-red-950/50';
  if (score >= threshold * 0.7) return 'text-amber-400 bg-amber-950/50';
  if (score >= threshold * 0.4) return 'text-yellow-400 bg-yellow-950/50';
  return 'text-green-400 bg-green-950/50';
};

const getScoreEmoji = (score: number, threshold: number) => {
  // Removed emojis for professional appearance
  if (score >= threshold) return 'JAILBREAK';
  if (score >= threshold * 0.7) return 'WARNING';
  if (score >= threshold * 0.4) return 'PARTIAL';
  return 'BLOCKED';
};

export const IterationResultsPanel: React.FC<IterationResultsPanelProps> = ({
  iterations,
  successThreshold = 7.0,
}) => {
  const [expandedIteration, setExpandedIteration] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<'cards' | 'table'>('cards');

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('de-DE', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const toggleExpand = (iterationNum: number) => {
    setExpandedIteration(expandedIteration === iterationNum ? null : iterationNum);
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 rounded-lg border border-slate-800 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-900/80 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold text-slate-200">Iteration Results</h3>
          <span className="text-xs text-slate-500 px-2 py-0.5 bg-slate-800 rounded-full">
            {iterations.length} iterations
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode('cards')}
            className={`px-2 py-1 text-xs rounded transition-colors ${
              viewMode === 'cards'
                ? 'bg-cyan-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            Cards
          </button>
          <button
            onClick={() => setViewMode('table')}
            className={`px-2 py-1 text-xs rounded transition-colors ${
              viewMode === 'table'
                ? 'bg-cyan-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            Table
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3">
        {iterations.length === 0 ? (
          <div className="flex items-center justify-center h-full text-slate-500">
            <span>No iterations completed yet</span>
          </div>
        ) : viewMode === 'cards' ? (
          <div className="space-y-3">
            {iterations.map((iter) => {
              const isExpanded = expandedIteration === iter.iteration_number;
              const scoreColor = getScoreColor(iter.judge_score, successThreshold);
              const scoreEmoji = getScoreEmoji(iter.judge_score, successThreshold);

              return (
                <div
                  key={iter.iteration_number}
                  className={`border rounded-lg overflow-hidden transition-all ${
                    iter.success
                      ? 'border-red-600 bg-red-950/20'
                      : 'border-slate-700 bg-slate-900/50'
                  }`}
                >
                  {/* Header */}
                  <div
                    className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-slate-800/50 transition-colors"
                    onClick={() => toggleExpand(iter.iteration_number)}
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-xl">{scoreEmoji}</span>
                      <span className="font-bold text-slate-200">#{iter.iteration_number}</span>
                    </div>

                    <span className="px-2 py-0.5 text-xs bg-slate-700 text-slate-300 rounded">
                      {iter.strategy}
                    </span>

                    <div className={`px-2 py-0.5 text-sm font-mono rounded ${scoreColor}`}>
                      Score: {iter.judge_score.toFixed(2)}
                    </div>

                    {/* Token badge */}
                    {iter.token_breakdown && iter.token_breakdown.total > 0 && (
                      <span className="text-xs text-slate-500">
                        {iter.token_breakdown.total} tokens
                      </span>
                    )}

                    <span className="text-xs text-slate-500">
                      {iter.latency_breakdown?.total_ms.toFixed(0) || iter.latency_ms.toFixed(0)}ms
                    </span>

                    <span className="text-xs text-slate-500 ml-auto">
                      {formatTimestamp(iter.timestamp)}
                    </span>

                    <span className="text-slate-400">{isExpanded ? '▼' : '▶'}</span>
                  </div>

                  {/* Expanded Content */}
                  {isExpanded && (
                    <div className="border-t border-slate-700 p-4 space-y-4">
                      {/* Prompt */}
                      <div>
                        <h5 className="text-xs font-semibold text-cyan-400 uppercase mb-2">
                          Attack Prompt
                        </h5>
                        <div className="bg-slate-800 rounded p-3 text-sm text-slate-300 font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
                          {iter.prompt}
                        </div>
                      </div>

                      {/* Response */}
                      <div>
                        <h5 className="text-xs font-semibold text-blue-400 uppercase mb-2">
                          Target Response
                        </h5>
                        <div className="bg-slate-800 rounded p-3 text-sm text-slate-300 font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
                          {iter.response}
                        </div>
                      </div>

                      {/* Judge Reasoning */}
                      {iter.judge_reasoning && (
                        <div>
                          <h5 className="text-xs font-semibold text-amber-400 uppercase mb-2">
                            Judge Reasoning
                          </h5>
                          <div className="bg-slate-800 rounded p-3 text-sm text-slate-300 whitespace-pre-wrap max-h-32 overflow-y-auto">
                            {iter.judge_reasoning}
                          </div>
                        </div>
                      )}

                      {/* Charts Section */}
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
                        {/* Latency Breakdown Chart */}
                        {iter.latency_breakdown && (
                          <LatencyBreakdownChart latency_breakdown={iter.latency_breakdown} />
                        )}

                        {/* Token Pie Chart */}
                        {iter.token_breakdown && iter.token_breakdown.total > 0 && (
                          <TokenPieChart token_breakdown={iter.token_breakdown} />
                        )}
                      </div>

                      {/* Judge Scores Radar (Full Width) */}
                      {iter.sub_scores && (
                        <JudgeScoresRadar
                          sub_scores={iter.sub_scores}
                          overall_score={iter.judge_score}
                          confidence={iter.confidence}
                        />
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          /* Table View */
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-900">
                <tr>
                  <th className="px-3 py-2 text-left text-slate-400">#</th>
                  <th className="px-3 py-2 text-left text-slate-400">Strategy</th>
                  <th className="px-3 py-2 text-left text-slate-400">Score</th>
                  <th className="px-3 py-2 text-left text-slate-400">Success</th>
                  <th className="px-3 py-2 text-left text-slate-400">Latency</th>
                  <th className="px-3 py-2 text-left text-slate-400">Time</th>
                </tr>
              </thead>
              <tbody>
                {iterations.map((iter) => {
                  const scoreColor = getScoreColor(iter.judge_score, successThreshold);
                  return (
                    <tr
                      key={iter.iteration_number}
                      className="border-t border-slate-800 hover:bg-slate-900/50 cursor-pointer"
                      onClick={() => toggleExpand(iter.iteration_number)}
                    >
                      <td className="px-3 py-2 text-slate-300">{iter.iteration_number}</td>
                      <td className="px-3 py-2">
                        <span className="px-2 py-0.5 text-xs bg-slate-700 text-slate-300 rounded">
                          {iter.strategy}
                        </span>
                      </td>
                      <td className="px-3 py-2">
                        <span className={`px-2 py-0.5 text-xs rounded ${scoreColor}`}>
                          {iter.judge_score.toFixed(2)}
                        </span>
                      </td>
                      <td className="px-3 py-2">
                        {iter.success ? (
                          <span className="text-red-400">Yes</span>
                        ) : (
                          <span className="text-green-400">No</span>
                        )}
                      </td>
                      <td className="px-3 py-2 text-slate-400">{iter.latency_ms.toFixed(0)}ms</td>
                      <td className="px-3 py-2 text-slate-500">
                        {formatTimestamp(iter.timestamp)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default IterationResultsPanel;
