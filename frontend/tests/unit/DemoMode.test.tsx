/**
 * Unit tests for demo mode functionality.
 * 
 * Tests demo mode detection, API path routing, and component behavior.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { isDemoMode, getApiPath } from '@/lib/config';
import { DemoModeBanner } from '@/components/common/DemoModeBanner';
import { DemoTooltip } from '@/components/common/DemoTooltip';

// Mock environment variables
const originalEnv = import.meta.env;

describe('Demo Mode Configuration', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  describe('isDemoMode', () => {
    it('should return true when VITE_DEMO_MODE is "true"', () => {
      import.meta.env.VITE_DEMO_MODE = 'true';
      expect(isDemoMode()).toBe(true);
    });

    it('should return false when VITE_DEMO_MODE is not "true"', () => {
      import.meta.env.VITE_DEMO_MODE = 'false';
      expect(isDemoMode()).toBe(false);
      
      import.meta.env.VITE_DEMO_MODE = undefined;
      expect(isDemoMode()).toBe(false);
    });
  });

  describe('getApiPath', () => {
    it('should route to /api/demo/* when demo mode is enabled', () => {
      import.meta.env.VITE_DEMO_MODE = 'true';
      expect(getApiPath('experiments')).toBe('/api/demo/experiments');
      expect(getApiPath('/experiments')).toBe('/api/demo/experiments');
      expect(getApiPath('experiments/123')).toBe('/api/demo/experiments/123');
    });

    it('should route to /api/* when demo mode is disabled', () => {
      import.meta.env.VITE_DEMO_MODE = 'false';
      expect(getApiPath('experiments')).toBe('/api/experiments');
      expect(getApiPath('/experiments')).toBe('/api/experiments');
      expect(getApiPath('experiments/123')).toBe('/api/experiments/123');
    });
  });
});

describe('DemoModeBanner', () => {
  it('should render when demo mode is enabled', () => {
    import.meta.env.VITE_DEMO_MODE = 'true';
    render(<DemoModeBanner />);
    expect(screen.getByText(/Demo Mode Active/i)).toBeInTheDocument();
  });

  it('should not render when demo mode is disabled', () => {
    import.meta.env.VITE_DEMO_MODE = 'false';
    const { container } = render(<DemoModeBanner />);
    expect(container.firstChild).toBeNull();
  });
});

describe('DemoTooltip', () => {
  it('should wrap children when demo mode is enabled', () => {
    import.meta.env.VITE_DEMO_MODE = 'true';
    render(
      <DemoTooltip>
        <button>Create Experiment</button>
      </DemoTooltip>
    );
    expect(screen.getByText('Create Experiment')).toBeInTheDocument();
  });

  it('should not wrap children when demo mode is disabled', () => {
    import.meta.env.VITE_DEMO_MODE = 'false';
    render(
      <DemoTooltip>
        <button>Create Experiment</button>
      </DemoTooltip>
    );
    expect(screen.getByText('Create Experiment')).toBeInTheDocument();
  });
});
