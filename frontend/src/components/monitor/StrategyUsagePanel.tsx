/**
 * StrategyUsagePanel - Displays strategy usage statistics
 * 
 * Shows which strategies were selected, which were used, and which were skipped.
 * Part of Phase 3: Strategy Selection & Rotation Fix.
 */

import React from 'react';

interface StrategyUsagePanelProps {
  selectedStrategies: string[];
  usedStrategies: Record<string, number>;
}

export const StrategyUsagePanel: React.FC<StrategyUsagePanelProps> = ({
  selectedStrategies,
  usedStrategies,
}) => {
  const skipped = selectedStrategies.filter(s => !usedStrategies[s]);
  const usageRate = selectedStrategies.length > 0 
    ? (Object.keys(usedStrategies).length / selectedStrategies.length) * 100 
    : 0;

  return (
    <div className="bg-slate-800 rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Strategy Usage</h3>
        <div className="text-sm text-slate-400">
          {usageRate.toFixed(1)}% Usage Rate
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="bg-slate-700 rounded p-3">
          <div className="text-xs text-slate-400 mb-1">Selected</div>
          <div className="text-2xl font-bold text-blue-400">{selectedStrategies.length}</div>
        </div>
        <div className="bg-slate-700 rounded p-3">
          <div className="text-xs text-slate-400 mb-1">Used</div>
          <div className="text-2xl font-bold text-green-400">{Object.keys(usedStrategies).length}</div>
        </div>
        <div className="bg-slate-700 rounded p-3">
          <div className="text-xs text-slate-400 mb-1">Skipped</div>
          <div className="text-2xl font-bold text-red-400">{skipped.length}</div>
        </div>
      </div>

      {skipped.length > 0 && (
        <div className="mt-4">
          <p className="text-sm text-slate-300 mb-2 font-medium">Skipped Strategies:</p>
          <div className="flex flex-wrap gap-2">
            {skipped.map((strategy) => (
              <span
                key={strategy}
                className="px-2 py-1 bg-red-900/30 text-red-300 rounded text-xs"
              >
                {strategy}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="mt-4">
        <p className="text-sm text-slate-300 mb-2 font-medium">Usage Distribution:</p>
        <div className="space-y-1 max-h-48 overflow-y-auto">
          {Object.entries(usedStrategies)
            .sort(([, a], [, b]) => b - a)
            .map(([strategy, count]) => (
              <div key={strategy} className="flex justify-between items-center text-xs">
                <span className="text-slate-400 truncate flex-1">{strategy}</span>
                <span className="text-slate-300 ml-2">{count}x</span>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};
