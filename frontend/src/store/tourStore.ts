/**
 * Guided tour store using Zustand.
 * Tracks tour state and persists completion to localStorage.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface TourStep {
  id: string;
  title: string;
  description: string;
  target: string; // CSS selector or data attribute
  position: 'top' | 'bottom' | 'left' | 'right';
}

interface TourState {
  hasSeenTour: boolean;
  isTourActive: boolean;
  currentStep: number;
  steps: TourStep[];
  startTour: () => void;
  endTour: () => void;
  nextStep: () => void;
  previousStep: () => void;
  skipTour: () => void;
  resetTour: () => void;
}

// Define the 4-step walkthrough
const TOUR_STEPS: TourStep[] = [
  {
    id: 'step-1-running',
    title: 'Running Experiment',
    description: 'This experiment is actively testing the target LLM with various attack strategies. Watch the progress in real-time.',
    target: '[data-tour="experiment-running"]',
    position: 'bottom',
  },
  {
    id: 'step-2-failed',
    title: 'Failed Experiment',
    description: 'This experiment encountered an error during execution. Click to view detailed error logs and troubleshooting information.',
    target: '[data-tour="experiment-failed"]',
    position: 'bottom',
  },
  {
    id: 'step-3-completed',
    title: 'Completed Experiment',
    description: 'This experiment has finished successfully. Click to explore discovered vulnerabilities and attack results.',
    target: '[data-tour="experiment-completed"]',
    position: 'bottom',
  },
  {
    id: 'step-4-monitoring',
    title: 'Real-Time Monitoring',
    description: 'Monitor experiment progress, view live attack iterations, and track vulnerability discoveries in the dashboard.',
    target: '[data-tour="monitoring-section"]',
    position: 'left',
  },
];

export const useTourStore = create<TourState>()(
  persist(
    (set, get) => ({
      hasSeenTour: false,
      isTourActive: false,
      currentStep: 0,
      steps: TOUR_STEPS,

      startTour: () => {
        set({
          isTourActive: true,
          currentStep: 0,
        });
      },

      endTour: () => {
        set({
          isTourActive: false,
          hasSeenTour: true,
          currentStep: 0,
        });
      },

      nextStep: () => {
        const { currentStep, steps } = get();
        if (currentStep < steps.length - 1) {
          set({ currentStep: currentStep + 1 });
        } else {
          get().endTour();
        }
      },

      previousStep: () => {
        const { currentStep } = get();
        if (currentStep > 0) {
          set({ currentStep: currentStep - 1 });
        }
      },

      skipTour: () => {
        set({
          isTourActive: false,
          hasSeenTour: true,
          currentStep: 0,
        });
      },

      resetTour: () => {
        set({
          hasSeenTour: false,
          isTourActive: true,
          currentStep: 0,
        });
      },
    }),
    {
      name: 'cerebro-tour',
      // Only persist hasSeenTour, not active state
      partialize: (state) => ({ hasSeenTour: state.hasSeenTour }),
    }
  )
);
