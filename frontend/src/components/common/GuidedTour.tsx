/**
 * Guided tour component for demo mode.
 * Implements a 4-step walkthrough highlighting key features.
 */

import { useEffect, useState, useCallback } from 'react';
import { useTourStore } from '@/store/tourStore';
import { Button } from '@/components/ui/button';
import { X, ChevronLeft, ChevronRight } from 'lucide-react';

export function GuidedTour() {
  const {
    isTourActive,
    currentStep,
    steps,
    nextStep,
    previousStep,
    skipTour,
    endTour,
  } = useTourStore();

  const [targetElement, setTargetElement] = useState<HTMLElement | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });

  const currentStepData = steps[currentStep];

  // Calculate tooltip position based on target element
  const calculatePosition = useCallback((target: HTMLElement, position: string) => {
    const rect = target.getBoundingClientRect();
    const tooltipWidth = 360; // Approximate tooltip width
    const tooltipHeight = 200; // Approximate tooltip height
    const offset = 20; // Spacing from target

    let top = 0;
    let left = 0;

    switch (position) {
      case 'bottom':
        top = rect.bottom + offset;
        left = rect.left + rect.width / 2 - tooltipWidth / 2;
        break;
      case 'top':
        top = rect.top - tooltipHeight - offset;
        left = rect.left + rect.width / 2 - tooltipWidth / 2;
        break;
      case 'left':
        top = rect.top + rect.height / 2 - tooltipHeight / 2;
        left = rect.left - tooltipWidth - offset;
        break;
      case 'right':
        top = rect.top + rect.height / 2 - tooltipHeight / 2;
        left = rect.right + offset;
        break;
    }

    // Keep tooltip within viewport
    const padding = 16;
    top = Math.max(padding, Math.min(top, window.innerHeight - tooltipHeight - padding));
    left = Math.max(padding, Math.min(left, window.innerWidth - tooltipWidth - padding));

    return { top, left };
  }, []);

  // Find and highlight target element
  useEffect(() => {
    if (!isTourActive || !currentStepData) {
      setTargetElement(null);
      return;
    }

    const findTarget = () => {
      const target = document.querySelector<HTMLElement>(currentStepData.target);
      if (target) {
        setTargetElement(target);
        const pos = calculatePosition(target, currentStepData.position);
        setTooltipPosition(pos);

        // Scroll target into view
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        // Retry after a short delay if target not found
        setTimeout(findTarget, 100);
      }
    };

    findTarget();
  }, [isTourActive, currentStep, currentStepData, calculatePosition]);

  // Handle window resize
  useEffect(() => {
    if (!targetElement || !currentStepData) return;

    const handleResize = () => {
      const pos = calculatePosition(targetElement, currentStepData.position);
      setTooltipPosition(pos);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [targetElement, currentStepData, calculatePosition]);

  // Handle escape key to skip tour
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isTourActive) {
        skipTour();
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isTourActive, skipTour]);

  if (!isTourActive || !currentStepData) {
    return null;
  }

  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <>
      {/* Overlay */}
      <div className="tour-overlay fixed inset-0 bg-black/50 z-40" />

      {/* Highlight */}
      {targetElement && (
        <div
          className="tour-highlight fixed z-50 pointer-events-none"
          style={{
            top: targetElement.getBoundingClientRect().top - 4,
            left: targetElement.getBoundingClientRect().left - 4,
            width: targetElement.getBoundingClientRect().width + 8,
            height: targetElement.getBoundingClientRect().height + 8,
          }}
        />
      )}

      {/* Tooltip */}
      <div
        className="tour-tooltip fixed z-50 bg-white dark:bg-gray-800 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 p-6 w-[360px]"
        style={{
          top: `${tooltipPosition.top}px`,
          left: `${tooltipPosition.left}px`,
        }}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="text-sm text-muted-foreground mb-1">
              Step {currentStep + 1} of {steps.length}
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {currentStepData.title}
            </h3>
          </div>
          <button
            onClick={skipTour}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 ml-2"
            aria-label="Skip tour"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-1 bg-gray-200 dark:bg-gray-700 rounded-full mb-4">
          <div
            className="h-1 bg-blue-600 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Content */}
        <p className="text-sm text-gray-700 dark:text-gray-300 mb-6">
          {currentStepData.description}
        </p>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            size="sm"
            onClick={previousStep}
            disabled={currentStep === 0}
            className="disabled:opacity-50"
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>

          <div className="flex items-center gap-1">
            {steps.map((_, index) => (
              <div
                key={index}
                className={`h-2 w-2 rounded-full transition-colors ${
                  index === currentStep
                    ? 'bg-blue-600'
                    : index < currentStep
                    ? 'bg-blue-300 dark:bg-blue-700'
                    : 'bg-gray-300 dark:bg-gray-600'
                }`}
              />
            ))}
          </div>

          {currentStep < steps.length - 1 ? (
            <Button variant="default" size="sm" onClick={nextStep}>
              Next
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          ) : (
            <Button variant="default" size="sm" onClick={endTour}>
              Finish
            </Button>
          )}
        </div>
      </div>
    </>
  );
}
