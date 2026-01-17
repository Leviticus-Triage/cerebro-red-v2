/**
 * Status badge component for experiment and vulnerability statuses.
 */

import { Badge } from '@/components/ui/badge';
import { getSeverityBadgeVariant } from '@/lib/utils';

interface StatusBadgeProps {
  status: string;
  type?: 'experiment' | 'vulnerability';
}

export function StatusBadge({ status, type = 'experiment' }: StatusBadgeProps) {
  if (type === 'vulnerability') {
    const variant = getSeverityBadgeVariant(status);
    return <Badge variant={variant}>{status.toUpperCase()}</Badge>;
  }

  // Experiment status
  const variantMap: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
    running: 'default',
    completed: 'default',
    paused: 'secondary',
    failed: 'destructive',
    pending: 'outline',
  };

  return <Badge variant={variantMap[status] || 'outline'}>{status.toUpperCase()}</Badge>;
}
