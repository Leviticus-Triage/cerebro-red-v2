/**
 * VerbositySelector - Professional dropdown for selecting verbosity level
 * 
 * Provides 4 verbosity levels with descriptions:
 * - Level 0: Silent - Errors Only
 * - Level 1: Basic - + Events & Progress
 * - Level 2: Detailed - + LLM Requests/Responses
 * - Level 3: Debug - + Full Code Flow
 */

import React from 'react';
import { Select } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';

interface VerbositySelectorProps {
  value: number;
  onChange: (level: number) => void;
  isConnected: boolean;
}

const VERBOSITY_LEVELS = [
  { 
    value: 0, 
    label: 'Silent', 
    description: 'Errors Only',
    color: 'bg-red-900/30 text-red-400 border-red-700',
    details: 'Only errors and critical failures are shown'
  },
  { 
    value: 1, 
    label: 'Basic', 
    description: '+ Events & Progress',
    color: 'bg-yellow-900/30 text-yellow-400 border-yellow-700',
    details: 'Includes iteration start/complete, progress updates, vulnerabilities'
  },
  { 
    value: 2, 
    label: 'Detailed', 
    description: '+ LLM I/O',
    color: 'bg-green-900/30 text-green-400 border-green-700',
    details: 'Includes LLM requests/responses, judge evaluations, attack mutations'
  },
  { 
    value: 3, 
    label: 'Debug', 
    description: '+ Code Flow',
    color: 'bg-blue-900/30 text-blue-400 border-blue-700',
    details: 'Includes strategy selection, mutation start/end, judge start/end, decision points'
  }
];

export const VerbositySelector: React.FC<VerbositySelectorProps> = ({ 
  value, 
  onChange, 
  isConnected 
}) => {
  const currentLevel = VERBOSITY_LEVELS.find(l => l.value === value) || VERBOSITY_LEVELS[0];
  
  const handleChange = (newValue: string) => {
    const level = parseInt(newValue, 10);
    if (level >= 0 && level <= 3) {
      onChange(level);
    }
  };
  
  return (
    <div className="flex items-center gap-4 p-4 bg-slate-900 rounded-lg border border-slate-800">
      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-slate-300">Verbosity:</label>
        <Select 
          value={value.toString()} 
          onChange={(e) => handleChange(e.target.value)}
          disabled={!isConnected}
          className="w-64 bg-slate-800 border-slate-700 text-slate-200"
        >
          {VERBOSITY_LEVELS.map(level => (
            <option key={level.value} value={level.value.toString()}>
              {level.label} - {level.description}
            </option>
          ))}
        </Select>
      </div>
      
      {currentLevel && (
        <Badge className={currentLevel.color}>
          {currentLevel.description}
        </Badge>
      )}
      
      {!isConnected && (
        <span className="text-xs text-slate-500 italic">
          Connect to experiment to change verbosity
        </span>
      )}
    </div>
  );
};
