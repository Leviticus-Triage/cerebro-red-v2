/**
 * frontend/src/components/common/DemoModeBanner.tsx
 * ====================================================
 *
 * Demo mode warning banner displayed at the top of the application.
 * Only visible when VITE_DEMO_MODE=true.
 */

import { isDemoMode } from '@/lib/config';
import { ExternalLink } from 'lucide-react';

export function DemoModeBanner() {
  // Don't render anything if demo mode is not enabled
  if (!isDemoMode) return null;

  return (
    <div className="bg-yellow-50 border-b-2 border-yellow-400 text-yellow-800 dark:bg-yellow-900/20 dark:border-yellow-600 dark:text-yellow-200 px-6 py-3">
      <div className="flex items-center justify-center gap-2 text-sm font-medium">
        <span className="text-lg" role="img" aria-label="Target">
          
        </span>
        <span className="font-bold">Demo Mode</span>
        <span className="hidden sm:inline">—</span>
        <span className="hidden sm:inline">
          Explore pre-configured experiments (read-only)
        </span>
        <a
          href="https://github.com/your-org/cerebro-red-v2#quick-start"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 underline hover:no-underline"
          aria-label="View Quick Start documentation"
        >
          <span>Deploy locally</span>
          <ExternalLink className="h-3 w-3" />
        </a>
      </div>
    </div>
  );
}
