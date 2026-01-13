import { render, screen, fireEvent } from '@testing-library/react';
import { LiveLogPanel } from '../LiveLogPanel';
import type { LiveLogEntry, TaskQueueItem, CodeFlowEvent } from '@/types/api';

describe('LiveLogPanel', () => {
  const mockLogs: LiveLogEntry[] = [
    {
      id: '1',
      timestamp: new Date().toISOString(),
      type: 'llm_request',
      role: 'attacker',
      provider: 'ollama',
      model: 'llama3.2',
      content: 'Test prompt',
      metadata: { prompt: 'Full test prompt here' }
    },
    {
      id: '2',
      timestamp: new Date().toISOString(),
      type: 'llm_response',
      role: 'target',
      provider: 'ollama',
      model: 'qwen2.5:3b',
      content: 'Test response',
      metadata: { response: 'Full test response here', latency_ms: 1500, tokens: 100 }
    },
    {
      id: '3',
      timestamp: new Date().toISOString(),
      type: 'judge',
      role: 'judge',
      content: 'Judge reasoning',
      metadata: { score: 5.5, reasoning: 'Test reasoning', success: false, latency_ms: 2000 }
    },
    {
      id: '4',
      timestamp: new Date().toISOString(),
      type: 'error',
      content: 'Test error message',
      metadata: { error_type: 'test_error' }
    }
  ];

  const mockTasks: TaskQueueItem[] = [
    {
      id: 'task-1',
      name: 'Iteration 1: Mutate Prompt',
      status: 'completed',
      iteration: 1,
      strategy: 'obfuscation_base64',
      startedAt: new Date().toISOString(),
      completedAt: new Date().toISOString(),
      queuePosition: 1
    },
    {
      id: 'task-2',
      name: 'Iteration 1: Query Target LLM',
      status: 'running',
      iteration: 1,
      startedAt: new Date().toISOString(),
      queuePosition: 2
    }
  ];

  const mockCodeFlowEvents: CodeFlowEvent[] = [
    {
      id: 'cf-1',
      timestamp: new Date().toISOString(),
      event_type: 'strategy_selection',
      iteration: 1,
      description: 'Selected strategy: obfuscation_base64'
    },
    {
      id: 'cf-2',
      timestamp: new Date().toISOString(),
      event_type: 'function_call',
      function_name: '_run_pair_loop',
      parameters: { iteration: 1 },
      result: 'success'
    }
  ];

  it('should render all 6 tabs', () => {
    render(<LiveLogPanel logs={mockLogs} tasks={mockTasks} codeFlowEvents={mockCodeFlowEvents} />);
    
    expect(screen.getByText(/Requests/)).toBeInTheDocument();
    expect(screen.getByText(/Responses/)).toBeInTheDocument();
    expect(screen.getByText(/Judge/)).toBeInTheDocument();
    expect(screen.getByText(/Tasks/)).toBeInTheDocument();
    expect(screen.getByText(/Code Flow/)).toBeInTheDocument();
    expect(screen.getByText(/Errors/)).toBeInTheDocument();
  });

  it('should filter logs by tab', () => {
    render(<LiveLogPanel logs={mockLogs} tasks={mockTasks} codeFlowEvents={mockCodeFlowEvents} />);
    
    // Click Requests tab
    fireEvent.click(screen.getByText(/Requests/));
    
    // Verify only request logs are shown (check for table headers)
    expect(screen.getByText('Prompt')).toBeInTheDocument();
    expect(screen.getByText('Model')).toBeInTheDocument();
  });

  it('should display correct counts in tab badges', () => {
    render(<LiveLogPanel logs={mockLogs} tasks={mockTasks} codeFlowEvents={mockCodeFlowEvents} />);
    
    // Check that badges show correct counts
    const requestsTab = screen.getByText(/Requests/).closest('button');
    expect(requestsTab).toHaveTextContent('1'); // 1 request log
    
    const responsesTab = screen.getByText(/Responses/).closest('button');
    expect(responsesTab).toHaveTextContent('1'); // 1 response log
    
    const tasksTab = screen.getByText(/Tasks/).closest('button');
    expect(tasksTab).toHaveTextContent('2'); // 2 tasks
  });

  it('should expand row on click', () => {
    render(<LiveLogPanel logs={mockLogs} />);
    
    // Click Requests tab first
    fireEvent.click(screen.getByText(/Requests/));
    
    // Find first data row and click it
    const rows = screen.getAllByRole('row');
    if (rows.length > 1) {
      fireEvent.click(rows[1]); // Skip header row
      
      // Verify expanded content is shown (syntax highlighter or full text)
      // The exact implementation depends on react-syntax-highlighter rendering
      expect(screen.getByText(/Full test prompt here/)).toBeInTheDocument();
    }
  });

  it('should display export buttons', () => {
    render(<LiveLogPanel logs={mockLogs} />);
    
    expect(screen.getByText(' JSON')).toBeInTheDocument();
    expect(screen.getByText(' CSV')).toBeInTheDocument();
  });

  it('should handle empty logs gracefully', () => {
    render(<LiveLogPanel logs={[]} tasks={[]} codeFlowEvents={[]} />);
    
    // All tabs should still be visible
    expect(screen.getByText(/Requests/)).toBeInTheDocument();
    expect(screen.getByText(/Responses/)).toBeInTheDocument();
    
    // Badges should show 0
    const requestsTab = screen.getByText(/Requests/).closest('button');
    expect(requestsTab).toHaveTextContent('0');
  });

  it('should display task status badges correctly', () => {
    render(<LiveLogPanel logs={[]} tasks={mockTasks} codeFlowEvents={[]} />);
    
    fireEvent.click(screen.getByText(/Tasks/));
    
    // Verify task statuses are displayed
    expect(screen.getByText(/completed/)).toBeInTheDocument();
    expect(screen.getByText(/running/)).toBeInTheDocument();
  });

  it('should display code flow events correctly', () => {
    render(<LiveLogPanel logs={[]} tasks={[]} codeFlowEvents={mockCodeFlowEvents} />);
    
    fireEvent.click(screen.getByText(/Code Flow/));
    
    // Verify code flow events are displayed
    expect(screen.getByText(/strategy_selection/)).toBeInTheDocument();
    expect(screen.getByText(/function_call/)).toBeInTheDocument();
  });

  it('should respect maxLogs limit', () => {
    const manyLogs: LiveLogEntry[] = Array.from({ length: 1000 }, (_, i) => ({
      id: `log-${i}`,
      timestamp: new Date().toISOString(),
      type: 'llm_request',
      content: `Log ${i}`
    }));

    render(<LiveLogPanel logs={manyLogs} maxLogs={500} />);
    
    fireEvent.click(screen.getByText(/Requests/));
    
    // Should only show 500 logs (maxLogs)
    const requestsTab = screen.getByText(/Requests/).closest('button');
    expect(requestsTab).toHaveTextContent('500');
  });
});
