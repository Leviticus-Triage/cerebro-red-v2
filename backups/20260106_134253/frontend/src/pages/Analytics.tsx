/**
 * Analytics page with aggregate statistics and charts.
 */

import { useVulnerabilityStatistics } from '@/hooks/useVulnerabilities';
import { useExperiments } from '@/hooks/useExperiments';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { StrategyDistributionChart } from '@/components/charts/StrategyDistributionChart';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

export function Analytics() {
  const { data: vulnStats, isLoading: vulnLoading, error } = useVulnerabilityStatistics();
  useExperiments(1, 100); // Prefetch experiments for potential use

  if (vulnLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Analytics</h1>
          <p className="text-muted-foreground">Aggregate statistics and insights</p>
        </div>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-red-500 text-center">
              Error loading statistics: {error instanceof Error ? error.message : 'Unknown error'}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const hasData = vulnStats && vulnStats.total_vulnerabilities > 0;
  const hasStrategyData = vulnStats?.by_strategy && 
    Object.values(vulnStats.by_strategy).some(count => count > 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="text-muted-foreground">Aggregate statistics and insights</p>
      </div>

      {!hasData ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground text-center py-8">
              No vulnerabilities found yet. Run experiments to see statistics.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Vulnerability Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Total:</span>
                  <span className="font-semibold">{vulnStats.total_vulnerabilities || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>Critical:</span>
                  <span className="font-semibold text-red-600">
                    {vulnStats.by_severity?.critical || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>High:</span>
                  <span className="font-semibold text-orange-500">
                    {vulnStats.by_severity?.high || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Medium:</span>
                  <span className="font-semibold text-yellow-500">
                    {vulnStats.by_severity?.medium || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Low:</span>
                  <span className="font-semibold text-blue-500">
                    {vulnStats.by_severity?.low || 0}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {hasStrategyData ? (
            <StrategyDistributionChart data={vulnStats.by_strategy} />
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Strategy Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground text-center py-8">
                  No strategy data available
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}

