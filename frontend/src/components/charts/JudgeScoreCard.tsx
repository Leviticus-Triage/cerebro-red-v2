/**
 * Judge score card component showing detailed score breakdown.
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { AttackIteration } from '@/types/api';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface JudgeScoreCardProps {
  iterations: AttackIteration[];
}

export function JudgeScoreCard({ iterations }: JudgeScoreCardProps) {
  if (iterations.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Judge Score Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No iteration data available
          </p>
        </CardContent>
      </Card>
    );
  }

  // Calculate statistics
  const scores = iterations.map((it) => it.judge_score);
  const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
  const maxScore = Math.max(...scores);
  const minScore = Math.min(...scores);
  const successfulCount = iterations.filter((it) => it.success).length;
  const successRate = (successfulCount / iterations.length) * 100;

  // Calculate trend (comparing last 3 vs first 3 iterations)
  const firstThree = scores.slice(0, 3);
  const lastThree = scores.slice(-3);
  const firstAvg = firstThree.reduce((a, b) => a + b, 0) / firstThree.length;
  const lastAvg = lastThree.reduce((a, b) => a + b, 0) / lastThree.length;
  const trend = lastAvg - firstAvg;
  const TrendIcon = trend > 0.5 ? TrendingUp : trend < -0.5 ? TrendingDown : Minus;
  const trendColor = trend > 0.5 ? 'text-green-500' : trend < -0.5 ? 'text-red-500' : 'text-gray-500';

  // Strategy effectiveness
  const strategyScores: Record<string, number[]> = {};
  iterations.forEach((it) => {
    if (!strategyScores[it.strategy_used]) {
      strategyScores[it.strategy_used] = [];
    }
    strategyScores[it.strategy_used].push(it.judge_score);
  });

  const strategyAvg: Record<string, number> = {};
  Object.entries(strategyScores).forEach(([strategy, scores]) => {
    strategyAvg[strategy] = scores.reduce((a, b) => a + b, 0) / scores.length;
  });

  const bestStrategy = Object.entries(strategyAvg).reduce((a, b) => 
    a[1] > b[1] ? a : b
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Judge Score Analysis</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Average Score</p>
            <p className="text-2xl font-bold">{avgScore.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Max Score</p>
            <p className="text-2xl font-bold text-green-600">{maxScore.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Min Score</p>
            <p className="text-2xl font-bold text-red-600">{minScore.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Success Rate</p>
            <p className="text-2xl font-bold">{successRate.toFixed(1)}%</p>
          </div>
        </div>

        <div className="flex items-center gap-2 pt-2 border-t">
          <span className="text-sm text-muted-foreground">Trend:</span>
          <TrendIcon className={`h-4 w-4 ${trendColor}`} />
          <span className={`text-sm font-medium ${trendColor}`}>
            {trend > 0 ? '+' : ''}{trend.toFixed(2)} points
          </span>
          <span className="text-xs text-muted-foreground">
            (comparing last 3 vs first 3 iterations)
          </span>
        </div>

        {bestStrategy && (
          <div className="pt-2 border-t">
            <p className="text-sm text-muted-foreground mb-2">Most Effective Strategy</p>
            <div className="flex items-center justify-between">
              <Badge variant="outline">{bestStrategy[0]}</Badge>
              <span className="text-sm font-semibold">
                Avg Score: {bestStrategy[1].toFixed(2)}
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

