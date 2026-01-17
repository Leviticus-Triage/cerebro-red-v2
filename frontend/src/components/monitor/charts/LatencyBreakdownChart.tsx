import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface LatencyBreakdownChartProps {
  latency_breakdown: {
    mutation_ms: number;
    target_ms: number;
    judge_ms: number;
    total_ms: number;
  };
}

export const LatencyBreakdownChart: React.FC<LatencyBreakdownChartProps> = ({
  latency_breakdown,
}) => {
  const data = [
    { name: 'Mutation', value: latency_breakdown.mutation_ms, fill: '#06b6d4' },
    { name: 'Target LLM', value: latency_breakdown.target_ms, fill: '#3b82f6' },
    { name: 'Judge LLM', value: latency_breakdown.judge_ms, fill: '#f59e0b' },
  ];

  return (
    <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
      <h5 className="text-xs font-semibold text-slate-400 uppercase mb-3">
        Latency Breakdown (Total: {latency_breakdown.total_ms}ms)
      </h5>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis type="number" stroke="#94a3b8" />
          <YAxis type="category" dataKey="name" stroke="#94a3b8" width={100} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
            labelStyle={{ color: '#e2e8f0' }}
          />
          <Bar dataKey="value" fill="#06b6d4" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
