/**
 * Tooltip component (ShadcnUI-style).
 *
 * Simple tooltip implementation for showing additional information on hover.
 */

import * as React from 'react';
import { cn } from '@/lib/utils';

interface TooltipProviderProps {
  children: React.ReactNode;
}

export const TooltipProvider: React.FC<TooltipProviderProps> = ({ children }) => {
  return <>{children}</>;
};

interface TooltipProps {
  children: React.ReactNode;
}

export const Tooltip: React.FC<TooltipProps> = ({ children }) => {
  return <div className="relative inline-block group">{children}</div>;
};

interface TooltipTriggerProps {
  children: React.ReactNode;
  asChild?: boolean;
}

export const TooltipTrigger: React.FC<TooltipTriggerProps> = ({ children, asChild }) => {
  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children, {
      className: cn('group', children.props.className),
    } as any);
  }
  return <div className="group">{children}</div>;
};

interface TooltipContentProps {
  children: React.ReactNode;
  className?: string;
  side?: 'top' | 'bottom' | 'left' | 'right';
}

export const TooltipContent: React.FC<TooltipContentProps> = ({
  children,
  className,
  side = 'top',
}) => {
  const sideClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  return (
    <div
      className={cn(
        'absolute z-50 hidden group-hover:block bg-slate-800 text-slate-200 px-3 py-2 rounded-lg shadow-lg text-xs max-w-xs',
        sideClasses[side],
        className
      )}
      role="tooltip"
    >
      {children}
      {/* Arrow */}
      <div
        className={cn(
          'absolute w-2 h-2 bg-slate-800 rotate-45',
          side === 'top' && 'top-full left-1/2 -translate-x-1/2 -mt-1',
          side === 'bottom' && 'bottom-full left-1/2 -translate-x-1/2 -mb-1',
          side === 'left' && 'left-full top-1/2 -translate-y-1/2 -ml-1',
          side === 'right' && 'right-full top-1/2 -translate-y-1/2 -mr-1'
        )}
      />
    </div>
  );
};
