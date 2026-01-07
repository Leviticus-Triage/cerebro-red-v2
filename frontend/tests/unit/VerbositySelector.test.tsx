/**
 * frontend/tests/unit/VerbositySelector.test.tsx
 * ===============================================
 * 
 * Unit tests for VerbositySelector component.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { VerbositySelector } from '@/components/monitor/VerbositySelector';

describe('VerbositySelector', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  it('should render all 4 verbosity levels', () => {
    render(<VerbositySelector value={2} onChange={mockOnChange} isConnected={true} />);
    
    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();
    
    // Check that all 4 levels are available
    expect(screen.getByText(/Silent/)).toBeInTheDocument();
    expect(screen.getByText(/Basic/)).toBeInTheDocument();
    expect(screen.getByText(/Detailed/)).toBeInTheDocument();
    expect(screen.getByText(/Debug/)).toBeInTheDocument();
  });

  it('should call onChange when level is changed', () => {
    render(<VerbositySelector value={1} onChange={mockOnChange} isConnected={true} />);
    
    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: '3' } });
    
    expect(mockOnChange).toHaveBeenCalledWith(3);
    expect(mockOnChange).toHaveBeenCalledTimes(1);
  });

  it('should be disabled when not connected', () => {
    render(<VerbositySelector value={2} onChange={mockOnChange} isConnected={false} />);
    
    const select = screen.getByRole('combobox');
    expect(select).toBeDisabled();
    
    // Should show connection message
    expect(screen.getByText(/Connect to experiment/)).toBeInTheDocument();
  });

  it('should show current level description', () => {
    render(<VerbositySelector value={2} onChange={mockOnChange} isConnected={true} />);
    
    // Should show badge with description
    expect(screen.getByText(/\+ LLM I\/O/)).toBeInTheDocument();
  });

  it('should display correct badge for each level', () => {
    const { rerender } = render(<VerbositySelector value={0} onChange={mockOnChange} isConnected={true} />);
    expect(screen.getByText(/Errors Only/)).toBeInTheDocument();
    
    rerender(<VerbositySelector value={1} onChange={mockOnChange} isConnected={true} />);
    expect(screen.getByText(/\+ Events & Progress/)).toBeInTheDocument();
    
    rerender(<VerbositySelector value={2} onChange={mockOnChange} isConnected={true} />);
    expect(screen.getByText(/\+ LLM I\/O/)).toBeInTheDocument();
    
    rerender(<VerbositySelector value={3} onChange={mockOnChange} isConnected={true} />);
    expect(screen.getByText(/\+ Code Flow/)).toBeInTheDocument();
  });

  it('should not call onChange when disabled', () => {
    render(<VerbositySelector value={2} onChange={mockOnChange} isConnected={false} />);
    
    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: '3' } });
    
    // onChange should not be called when disabled
    expect(mockOnChange).not.toHaveBeenCalled();
  });
});
