/**
 * Experiment list component.
 */

import { useExperiments } from '@/hooks/useExperiments';
import { ExperimentCard } from './ExperimentCard';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState } from 'react';

export function ExperimentList() {
  const [page, setPage] = useState(1);
  const { data, isLoading, error } = useExperiments(page, 20);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">Failed to load experiments</p>
      </div>
    );
  }

  const experiments = data?.items || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / 20);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Experiments</h1>
          <p className="text-muted-foreground">Manage and monitor PAIR experiments</p>
        </div>
        <Link to="/experiments/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Experiment
          </Button>
        </Link>
      </div>

      {experiments.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No experiments yet. Create your first one!</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {experiments.map((experiment) => (
              <ExperimentCard key={experiment.experiment_id} experiment={experiment} />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="outline"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {page} of {totalPages}
              </span>
              <Button
                variant="outline"
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

