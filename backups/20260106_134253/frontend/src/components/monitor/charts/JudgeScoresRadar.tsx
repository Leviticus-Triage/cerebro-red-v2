import React from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts';

interface JudgeScoresRadarProps {
  sub_scores: {
    jailbreak_success: number;
    harmful_content: number;
    hallucination: number;
    bias: number;
    logical_consistency: number;
    sycophancy: number;
    policy_violation: number;
  };
  overall_score: number;
  confidence?: number;
}

export const JudgeScoresRadar: React.FC<JudgeScoresRadarProps> = ({ sub_scores, overall_score, confidence }) => {
  const data = [
    { metric: 'Jailbreak', score: sub_scores.jailbreak_success, fullMark: 10 },
    { metric: 'Harmful', score: sub_scores.harmful_content, fullMark: 10 },
    { metric: 'Hallucination', score: sub_scores.hallucination, fullMark: 10 },
    { metric: 'Bias', score: sub_scores.bias, fullMark: 10 },
    { metric: 'Logic', score: sub_scores.logical_consistency, fullMark: 10 },
    { metric: 'Sycophancy', score: sub_scores.sycophancy, fullMark: 10 },
    { metric: 'Policy', score: sub_scores.policy_violation, fullMark: 10 }
  ];

  return (
    <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
      <div className="flex items-center justify-between mb-3">
        <h5 className="text-xs font-semibold text-slate-400 uppercase">
          Judge Evaluation (7 Criteria)
        </h5>
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400">Overall:</span>
          <span className="font-bold text-amber-400">{overall_score.toFixed(2)}/10</span>
          {confidence && (
            <>
              <span className="text-slate-500">|</span>
              <span className="text-slate-400">Confidence:</span>
              <span className="text-cyan-400">{(confidence * 100).toFixed(0)}%</span>
            </>
          )}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={250}>
        <RadarChart data={data}>
          <PolarGrid stroke="#475569" />
          <PolarAngleAxis dataKey="metric" stroke="#94a3b8" tick={{ fontSize: 11 }} />
          <PolarRadiusAxis angle={90} domain={[0, 10]} stroke="#64748b" />
          <Radar name="Score" dataKey="score" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.6} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
            labelStyle={{ color: '#e2e8f0' }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};
