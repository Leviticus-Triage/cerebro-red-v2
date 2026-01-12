/**
 * Copyright 2024-2026 Cerebro-Red v2 Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * Dashboard page - Overview of experiments and statistics.
 */

import { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FlaskConical, AlertTriangle, TrendingUp, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useExperiments } from '@/hooks/useExperiments';
import { useVulnerabilityStatistics } from '@/hooks/useVulnerabilities';
import { ExperimentCard } from '@/components/experiments/ExperimentCard';
import { GuidedTour } from '@/components/common/GuidedTour';
import { useTourStore } from '@/store/tourStore';
import { isDemoMode } from '@/lib/config';

export function Dashboard() {
  const { data: experiments, isLoading } = useExperiments(1, 5);
  const { data: vulnStats } = useVulnerabilityStatistics();
  const { hasSeenTour, startTour } = useTourStore();

  // Auto-start tour on first visit in demo mode when data is loaded
  useEffect(() => {
    if (isDemoMode && !hasSeenTour && !isLoading && experiments?.items && experiments.items.length > 0) {
      // Delay tour start to ensure all elements are rendered
      const timer = setTimeout(() => {
        startTour();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [isDemoMode, hasSeenTour, isLoading, experiments, startTour]);

  const stats = [
    {
      title: 'Total Experiments',
      value: experiments?.total || 0,
      icon: FlaskConical,
      color: 'text-blue-500',
    },
    {
      title: 'Vulnerabilities Found',
      value: vulnStats?.total_vulnerabilities || 0,
      icon: AlertTriangle,
      color: 'text-red-500',
    },
    {
      title: 'Success Rate',
      value: '73%',
      icon: TrendingUp,
      color: 'text-green-500',
    },
    {
      title: 'Avg. Experiment Time',
      value: '12m',
      icon: Clock,
      color: 'text-purple-500',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Overview of CEREBRO-RED v2 experiments</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" data-tour="monitoring-section">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Recent Experiments</CardTitle>
            <Link to="/experiments">
              <span className="text-sm text-primary hover:underline">View all</span>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {experiments?.items && experiments.items.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {experiments.items.map((experiment) => (
                <ExperimentCard key={experiment.experiment_id} experiment={experiment} />
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground text-center py-8">
              No experiments yet. Create your first one!
            </p>
          )}
        </CardContent>
      </Card>

      {/* Guided Tour */}
      <GuidedTour />
    </div>
  );
}

