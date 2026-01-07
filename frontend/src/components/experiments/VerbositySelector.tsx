/**
 * Verbosity Level Selector component.
 * 
 * Allows users to set the verbosity level for experiment monitoring.
 */

import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface VerbositySelectorProps {
  value: number;
  onChange: (value: number) => void;
}

const VERBOSITY_LEVELS = [
  {
    level: 0,
    name: 'Silent',
    description: 'Only critical errors and final results',
  },
  {
    level: 1,
    name: 'Basic',
    description: 'Progress updates and iteration results',
  },
  {
    level: 2,
    name: 'Detailed',
    description: 'LLM requests/responses, judge evaluations, task queue',
  },
  {
    level: 3,
    name: 'Debug',
    description: 'Full code-flow tracking, function calls, parameters',
  }
];

export function VerbositySelector({ value, onChange }: VerbositySelectorProps) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          Verbosity Level
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label className="text-sm font-medium text-slate-300">
            Select monitoring detail level
          </Label>
          <div className="grid grid-cols-1 gap-2">
            {VERBOSITY_LEVELS.map(({ level, name, description }) => (
              <button
                key={level}
                type="button"
                onClick={() => onChange(level)}
                className={`
                  p-3 rounded-lg border-2 transition-all text-left
                  ${value === level
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-slate-600 bg-slate-700 hover:border-slate-500'
                  }
                `}
              >
                <div className="flex items-start gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-white">
                        Level {level}: {name}
                      </span>
                      {value === level && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500 text-white">
                          Active
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-slate-400 mt-1">
                      {description}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-slate-700/50 rounded-lg p-3 border border-slate-600">
          <p className="text-xs text-slate-300">
            <strong>Tip:</strong> Higher verbosity levels provide more insight but may impact performance.
            Use Level 2-3 for debugging, Level 1 for production monitoring.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
