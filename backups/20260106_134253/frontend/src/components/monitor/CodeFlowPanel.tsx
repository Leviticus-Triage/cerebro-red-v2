/**
 * CodeFlowPanel - Displays code execution flow for verbosity level 3
 * 
 * Shows:
 * - Function calls with parameters
 * - Strategy selections with reasoning
 * - Mutation/Judge start/end events
 * - Decision points (if/else, loops)
 * - Execution timeline
 */

import React from 'react';
import type { CodeFlowEvent } from '@/types/api';

interface CodeFlowPanelProps {
  events: CodeFlowEvent[];
}

const CodeFlowPanel: React.FC<CodeFlowPanelProps> = ({ events }) => {
  const getEventIcon = (_eventType: string) => {
    // Removed emojis for professional appearance
    return '';
  };

  const getEventColor = (eventType: string) => {
    switch (eventType) {
      case 'strategy_selection': return 'text-cyan-400';
      case 'mutation_start': return 'text-yellow-400';
      case 'mutation_end': return 'text-green-400';
      case 'judge_start': return 'text-purple-400';
      case 'judge_end': return 'text-blue-400';
      case 'decision_point': return 'text-orange-400';
      case 'function_call': return 'text-indigo-400';
      default: return 'text-slate-400';
    }
  };

  if (events.length === 0) {
    return (
      <div className="flex items-center justify-center h-full bg-slate-900 rounded-lg border border-slate-800">
        <div className="text-center text-slate-500">
          <p className="text-lg mb-2">No code-flow events yet</p>
          <p className="text-sm">
            Code-flow tracking requires <span className="text-cyan-400 font-mono">verbosity=3</span>
          </p>
          <p className="text-xs mt-2 text-slate-600">
            Set <span className="font-mono">CEREBRO_VERBOSITY=3</span> in backend .env
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-slate-900 rounded-lg border border-slate-800 overflow-hidden flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 bg-slate-800 border-b border-slate-700 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-200">
          Code Flow Execution ({events.length} events)
        </h3>
        <span className="text-xs text-slate-500">Verbosity Level 3</span>
      </div>

      {/* Events List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {events.map((event, index) => (
          <div
            key={event.id || index}
            className="bg-slate-800 rounded-lg p-3 border border-slate-700 hover:border-slate-600 transition-colors"
          >
            {/* Event Header */}
            <div className="flex items-start gap-3">
              <span className="text-2xl">{getEventIcon(event.event_type)}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-sm font-semibold ${getEventColor(event.event_type)}`}>
                    {event.event_type.replace(/_/g, ' ').toUpperCase()}
                  </span>
                  {event.iteration && (
                    <span className="text-xs text-slate-500">
                      Iteration {event.iteration}
                    </span>
                  )}
                  <span className="text-xs text-slate-600 ml-auto">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                {/* Event-Specific Content */}
                {event.event_type === 'strategy_selection' && (
                  <div className="space-y-1">
                    <p className="text-sm text-slate-300">
                      Strategy: <span className="text-cyan-400 font-mono">{event.strategy}</span>
                    </p>
                    {event.reasoning && (
                      <p className="text-xs text-slate-400">{event.reasoning}</p>
                    )}
                    {event.previous_score !== undefined && (
                      <p className="text-xs text-slate-500">
                        Previous Score: {event.previous_score.toFixed(2)} | Threshold: {event.threshold?.toFixed(2)}
                      </p>
                    )}
                  </div>
                )}

                {event.event_type === 'mutation_start' && (
                  <div className="space-y-1">
                    <p className="text-sm text-slate-300">
                      Strategy: <span className="text-yellow-400 font-mono">{event.strategy}</span>
                    </p>
                    <p className="text-xs text-slate-400 font-mono truncate">
                      {event.original_prompt}
                    </p>
                  </div>
                )}

                {event.event_type === 'mutation_end' && (
                  <div className="space-y-1">
                    <p className="text-sm text-slate-300">
                      Mutated in <span className="text-green-400">{event.latency_ms?.toFixed(0)}ms</span>
                    </p>
                    <p className="text-xs text-slate-400 font-mono truncate">
                      {event.mutated_prompt}
                    </p>
                  </div>
                )}

                {event.event_type === 'judge_start' && (
                  <div className="space-y-1">
                    <p className="text-sm text-slate-300">Evaluating target response...</p>
                    <p className="text-xs text-slate-400 font-mono truncate">
                      Response: {event.target_response}
                    </p>
                  </div>
                )}

                {event.event_type === 'judge_end' && (
                  <div className="space-y-1">
                    <p className="text-sm text-slate-300">
                      Score: <span className="text-blue-400 font-bold">{event.overall_score?.toFixed(2)}/10</span>
                      <span className="text-slate-500 ml-2">({event.latency_ms?.toFixed(0)}ms)</span>
                    </p>
                    {event.all_scores && (
                      <div className="grid grid-cols-2 gap-1 text-xs text-slate-500 mt-2">
                        {Object.entries(event.all_scores).map(([key, value]) => (
                          <div key={key}>
                            {key}: <span className="text-slate-400">{(value as number).toFixed(1)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    {event.reasoning && (
                      <p className="text-xs text-slate-400 mt-1">{event.reasoning}</p>
                    )}
                  </div>
                )}

                {event.event_type === 'decision_point' && (
                  <div className="space-y-1">
                    <p className="text-sm text-slate-300">
                      {event.decision_result ? 'PASS' : 'FAIL'} {event.description}
                    </p>
                    <p className="text-xs text-slate-400 font-mono">
                      Condition: {event.condition}
                    </p>
                  </div>
                )}

                {event.event_type === 'function_call' && (
                  <div className="space-y-2">
                    <p className="text-sm text-slate-300">
                      Function: <span className="text-indigo-400 font-mono">{event.function_name}</span>
                    </p>
                    {event.parameters && Object.keys(event.parameters).length > 0 && (
                      <div className="bg-slate-900 rounded p-2 border border-slate-700">
                        <p className="text-xs text-slate-400 mb-1">Parameters:</p>
                        <pre className="text-xs text-slate-300 font-mono overflow-x-auto">
                          {JSON.stringify(event.parameters, null, 2)}
                        </pre>
                      </div>
                    )}
                    {event.result !== undefined && (
                      <div className="bg-slate-900 rounded p-2 border border-slate-700">
                        <p className="text-xs text-slate-400 mb-1">Result:</p>
                        <pre className="text-xs text-slate-300 font-mono overflow-x-auto">
                          {typeof event.result === 'string' 
                            ? event.result 
                            : JSON.stringify(event.result, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CodeFlowPanel;
