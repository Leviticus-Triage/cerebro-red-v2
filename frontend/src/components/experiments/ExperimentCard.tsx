/**
 * Experiment card component for listing experiments.
 */

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { StatusBadge } from '@/components/common/StatusBadge';
import { formatDate } from '@/lib/utils';
import type { ExperimentResponse } from '@/types/api';
import { Clock, FlaskConical, Repeat, Pause, Play, Square } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from '@/lib/toast';

interface ExperimentCardProps {
  experiment: ExperimentResponse;
}

export function ExperimentCard({ experiment }: ExperimentCardProps) {
  const navigate = useNavigate();
  const [isRepeating, setIsRepeating] = useState(false);

  const handleRepeat = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isRepeating) return;
    
    setIsRepeating(true);
    try {
      const newExperiment = await apiClient.repeatExperiment(experiment.experiment_id);
      toast.success(`Experiment "${newExperiment.name}" erstellt`);
      // Navigate to the new experiment
      navigate(`/experiments/${newExperiment.experiment_id}`);
    } catch (error) {
      toast.error(`Fehler beim Wiederholen des Experiments: ${error instanceof Error ? error.message : 'Unbekannter Fehler'}`);
    } finally {
      setIsRepeating(false);
    }
  };

  return (
    <Link to={`/experiments/${experiment.experiment_id}`} className="block">
      <Card className="hover:shadow-lg transition-shadow cursor-pointer">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="flex items-center gap-2">
                <FlaskConical className="h-5 w-5" />
                {experiment.name}
              </CardTitle>
              {experiment.description && (
                <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                  {experiment.description}
                </p>
              )}
            </div>
            <StatusBadge status={experiment.status} />
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <span>{formatDate(experiment.created_at)}</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">
                {experiment.strategies.length} strategies
              </Badge>
              <div className="flex items-center gap-1">
                {experiment.status === 'running' && (
                  <div title="Pause">
                    <Pause className="h-3.5 w-3.5 text-muted-foreground" />
                  </div>
                )}
                {experiment.status === 'paused' && (
                  <div title="Resume">
                    <Play className="h-3.5 w-3.5 text-muted-foreground" />
                  </div>
                )}
                {(experiment.status === 'running' || experiment.status === 'paused') && (
                  <div title="Stop">
                    <Square className="h-3.5 w-3.5 text-muted-foreground" />
                  </div>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleRepeat}
                  disabled={isRepeating}
                  className="h-7 px-2"
                  title="Experiment wiederholen"
                >
                  <Repeat className={`h-3.5 w-3.5 ${isRepeating ? 'animate-spin' : ''}`} />
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

