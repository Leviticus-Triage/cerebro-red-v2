/**
 * frontend/src/components/common/DemoTooltip.tsx
 * =================================================
 *
 * Reusable tooltip wrapper for demo mode restrictions.
 * Automatically shows tooltip only when demo mode is enabled.
 */

import { ReactNode } from 'react';
import { isDemoMode } from '@/lib/config';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

interface DemoTooltipProps {
  children: ReactNode;
  message?: string;
  side?: 'top' | 'right' | 'bottom' | 'left';
}

export function DemoTooltip({
  children,
  message = 'Demo mode is read-only. Deploy locally to perform this action.',
  side = 'top',
}: DemoTooltipProps) {
  // If not in demo mode, render children without tooltip
  if (!isDemoMode) {
    return <>{children}</>;
  }

  // In demo mode, wrap with tooltip
  return (
    <Tooltip>
      <TooltipTrigger asChild>{children}</TooltipTrigger>
      <TooltipContent side={side} className="max-w-xs">
        <p className="text-sm">{message}</p>
      </TooltipContent>
    </Tooltip>
  );
}
