/**
 * Header component for the application.
 */

import { Moon, Sun, Settings, HelpCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useThemeStore } from '@/store/themeStore';
import { useTourStore } from '@/store/tourStore';
import { isDemoMode } from '@/lib/config';

export function Header() {
  const { theme, toggleTheme } = useThemeStore();
  const { resetTour } = useTourStore();

  return (
    <header className="border-b bg-background">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold">CEREBRO-RED v2</h1>
          <span className="text-sm text-muted-foreground">Research Edition</span>
        </div>
        <div className="flex items-center gap-2">
          {isDemoMode && (
            <Button
              variant="ghost"
              size="icon"
              onClick={resetTour}
              title="Restart guided tour"
              aria-label="Restart guided tour"
            >
              <HelpCircle className="h-5 w-5" />
            </Button>
          )}
          <Button variant="ghost" size="icon" onClick={toggleTheme}>
            {theme === 'light' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
          </Button>
          <Button variant="ghost" size="icon">
            <Settings className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}

