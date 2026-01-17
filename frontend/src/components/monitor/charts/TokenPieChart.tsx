import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface TokenPieChartProps {
  token_breakdown: {
    attacker: number;
    target: number;
    judge: number;
    total: number;
  };
}

const COLORS = ['#ef4444', '#3b82f6', '#f59e0b'];

export const TokenPieChart: React.FC<TokenPieChartProps> = ({ token_breakdown }) => {
  const data = [
    { name: 'Attacker', value: token_breakdown.attacker },
    { name: 'Target', value: token_breakdown.target },
    { name: 'Judge', value: token_breakdown.judge },
  ].filter((d) => d.value > 0); // Only show non-zero

  return (
    <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
      <h5 className="text-xs font-semibold text-slate-400 uppercase mb-3">
        Token Usage (Total: {token_breakdown.total})
      </h5>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((_entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
