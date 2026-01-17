/**
 * Mutation timeline chart showing prompt mutations over iterations.
 */

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
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { AttackIteration } from '@/types/api';

interface MutationTimelineProps {
  iterations: AttackIteration[];
}

export function MutationTimeline({ iterations }: MutationTimelineProps) {
  // Transform data to show mutation count and strategy changes over time
  const data = iterations.map((it, index) => {
    const previousIterations = iterations.slice(0, index);
    const strategyCount = previousIterations.filter(
      (prev) => prev.strategy_used === it.strategy_used
    ).length;

    return {
      iteration: it.iteration_number,
      timestamp: new Date(it.timestamp).getTime(),
      strategy: it.strategy_used,
      strategyCount: strategyCount + 1,
      score: it.judge_score,
    };
  });

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Mutation Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No iteration data available
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Mutation Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="iteration"
              label={{ value: 'Iteration', position: 'insideBottom', offset: -5 }}
            />
            <YAxis
              yAxisId="left"
              label={{ value: 'Strategy Count', angle: -90, position: 'insideLeft' }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              domain={[0, 10]}
              label={{ value: 'Judge Score', angle: 90, position: 'insideRight' }}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload as any;
                  return (
                    <div className="bg-background border rounded-lg p-3 shadow-lg">
                      <p className="font-semibold">Iteration {data.iteration}</p>
                      <p className="text-sm">Strategy: {data.strategy}</p>
                      <p className="text-sm">Strategy Count: {data.strategyCount}</p>
                      <p className="text-sm">Judge Score: {data.score.toFixed(2)}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="strategyCount"
              stroke="#8b5cf6"
              strokeWidth={2}
              name="Strategy Usage Count"
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="score"
              stroke="#3b82f6"
              strokeWidth={2}
              name="Judge Score"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
