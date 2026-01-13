/**
 * Copyright 2024-2026 Cerebro-Red v2 Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * ExperimentMonitor - Live monitoring page for experiment execution
 * 
 * Provides real-time visibility into:
 * - LLM requests/responses (Attacker, Target, Judge)
 * - Iteration progress and results
 * - Task queue status
 * - Scoring and rankings
 */

import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { wsClient } from '@/lib/websocket/client';
import { apiClient } from '@/lib/api/client';
import {
  LiveLogPanel,
  TaskQueuePanel,
  IterationResultsPanel,
  ProgressOverview,
  CodeFlowPanel,
  FailureAnalysisPanel,
  StrategyUsagePanel,
  VerbositySelector,
} from '@/components/monitor';
import type {
  WSMessage,
  LiveLogEntry,
  TaskQueueItem,
  IterationResult,
  CodeFlowEvent,
  ExperimentResponse,
  FailureAnalysis,
  VulnerabilityFinding,
} from '@/types/api';
import { ExperimentStatus } from '@/types/api';
import { useExperimentProgress } from '@/hooks/useExperimentProgress';

const ExperimentMonitor: React.FC = () => {
  const { experimentId } = useParams<{ experimentId: string }>();
  const navigate = useNavigate();
  
  // State
  const [experiment, setExperiment] = useState<ExperimentResponse | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [logs, setLogs] = useState<LiveLogEntry[]>([]);
  const [tasks, setTasks] = useState<TaskQueueItem[]>([]);
  const [iterations, setIterations] = useState<IterationResult[]>([]);
  const [backendStatus, setBackendStatus] = useState<ExperimentStatus>('pending' as ExperimentStatus);
  const [currentIteration, setCurrentIteration] = useState(0);
  const [totalIterations, setTotalIterations] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [successfulIterations, setSuccessfulIterations] = useState(0);
  const [vulnerabilitiesFound, setVulnerabilitiesFound] = useState(0);
  const [activeTab, setActiveTab] = useState<'logs' | 'iterations' | 'tasks' | 'code-flow' | 'strategy-usage'>('logs');
  
  // Load verbosity from localStorage (persist across page reloads)
  const getStoredVerbosity = (expId: string | undefined): number => {
    if (!expId) return 2; // Default if no experiment ID
    try {
      const stored = localStorage.getItem(`verbosity_${expId}`);
      if (stored !== null) {
        const parsed = parseInt(stored, 10);
        if (!isNaN(parsed) && parsed >= 0 && parsed <= 3) {
          return parsed;
        }
      }
    } catch (error) {
      console.error('Failed to load verbosity from localStorage:', error);
    }
    // Default to 2 (Detailed) if no stored value
    return 2;
  };
  
  const [verbosity, setVerbosity] = useState<number>(getStoredVerbosity(experimentId));
  const [codeFlowEvents, setCodeFlowEvents] = useState<CodeFlowEvent[]>([]);
  const [failureAnalysis, setFailureAnalysis] = useState<FailureAnalysis | null>(null);
  const [showFailureModal, setShowFailureModal] = useState(false);
  // Strategy usage tracking (Phase 3)
  const [selectedStrategies, setSelectedStrategies] = useState<string[]>([]);
  const [usedStrategies, setUsedStrategies] = useState<Record<string, number>>({});
  
  // Use centralized progress hook
  const { progressPercent: calculatedProgress, displayStatus } = useExperimentProgress({
    currentIteration,
    totalIterations,
    backendStatus,
  });
  
  // Use calculated values
  const status = displayStatus;
  const progressPercent = calculatedProgress;
  
  const logIdCounter = useRef(0);

  // Generate unique log ID
  const generateLogId = () => {
    logIdCounter.current += 1;
    return `log-${Date.now()}-${logIdCounter.current}`;
  };

  // Add log entry (append to existing logs, keep ALL logs for complete history)
  const addLog = useCallback((entry: Omit<LiveLogEntry, 'id'>) => {
    console.log('[MONITOR] ========== addLog CALLED ==========');
    console.log('[MONITOR] Entry type:', entry.type, 'Content:', entry.content?.slice(0, 100));
    
    const newLog = { ...entry, id: generateLogId() };
    console.log('[MONITOR] Generated log ID:', newLog.id);
    
    setLogs((prev) => {
      const updated = [...prev, newLog];
      console.log('[MONITOR] Logs array updated. Old length:', prev.length, 'New length:', updated.length);
      console.log('[MONITOR] New log:', newLog);
      return updated;
    });
    
    console.log('[MONITOR] ========== addLog COMPLETE ==========');
  }, []);

  // Handle verbosity change
  const handleVerbosityChange = useCallback((newVerbosity: number) => {
    setVerbosity(newVerbosity);
    
    // Persist verbosity level to localStorage (per experiment)
    try {
      if (experimentId) {
        localStorage.setItem(`verbosity_${experimentId}`, newVerbosity.toString());
      }
    } catch (error) {
      console.error('Failed to save verbosity to localStorage:', error);
    }
    
    // Send control message to backend
    if (wsClient.isConnected()) {
      wsClient.setVerbosity(newVerbosity);
    }
  }, [experimentId]);

  // Handle WebSocket messages
  const handleMessage = useCallback((message: WSMessage) => {
    console.log('[MONITOR] ========== handleMessage CALLED ==========');
    console.log('[MONITOR] Message type:', message.type);
    console.log('[MONITOR] Message:', message);
    
    const timestamp = message.timestamp || new Date().toISOString();

    switch (message.type) {
      case 'connected':
        setIsConnected(true);
        // Preserve localStorage verbosity preference - do NOT overwrite with server default
        if ('verbosity' in message && typeof message.verbosity === 'number') {
          const storedVerbosity = getStoredVerbosity(experimentId);
          const serverVerbosity = message.verbosity || 2;
          
          // Use stored verbosity if it exists and is >= server, otherwise use max of both
          const targetVerbosity = Math.max(storedVerbosity, serverVerbosity);
          setVerbosity(targetVerbosity);
          
          // If stored verbosity is higher than server, push it to server
          if (storedVerbosity > serverVerbosity && wsClient.isConnected()) {
            wsClient.setVerbosity(storedVerbosity);
          }
          
          // Do NOT save server verbosity to localStorage here - preserve user preference
          // Only 'verbosity_updated' handler saves to localStorage (confirms server sync)
        }
        addLog({
          timestamp,
          type: 'info',
          content: 'Connected to experiment stream',
        });
        break;

      case 'verbosity_updated':
        if ('verbosity' in message && typeof message.verbosity === 'number') {
          setVerbosity(message.verbosity);
          // Save received verbosity back to localStorage
          try {
            if (experimentId) {
              localStorage.setItem(`verbosity_${experimentId}`, message.verbosity.toString());
            }
          } catch (error) {
            console.error('Failed to save verbosity to localStorage:', error);
          }
          addLog({
            timestamp,
            type: 'info',
            content: `Verbosity level changed to ${message.verbosity}`,
          });
        }
        break;

      case 'progress':
        if (message.iteration !== undefined) {
          const iter = message.iteration;
          const total = message.total_iterations || totalIterations;
          // Update iteration counts (hook will calculate progress)
          setCurrentIteration(Math.min(iter, total));
        }
        if (message.total_iterations !== undefined) {
          setTotalIterations(message.total_iterations);
        }
        if (message.elapsed_time_seconds !== undefined) {
          setElapsedSeconds(message.elapsed_time_seconds);
        }
        // Update backend status
        setBackendStatus('running' as ExperimentStatus);
        break;

      case 'iteration_start':
        addLog({
          timestamp,
          type: 'info',
          content: `Starting iteration ${message.iteration}/${message.total_iterations} with ${message.strategy_used}`,
        });
        // Add to task queue
        setTasks((prev) => [
          ...prev,
          {
            id: `iter-${message.iteration}`,
            name: `Iteration ${message.iteration}`,
            status: 'running',
            iteration: message.iteration,
            strategy: message.strategy_used,
            startedAt: timestamp,
          },
        ]);
        break;

      case 'llm_request':
        console.log('[MONITOR] Processing llm_request');
        console.log('[MONITOR] Role:', message.role, 'Prompt length:', message.prompt?.length);
        
        const requestLog = {
          timestamp,
          type: 'llm_request' as const,
          role: message.role,
          provider: message.provider,
          model: message.model,
          content: `${message.role?.toUpperCase()} Request: ${message.prompt?.slice(0, 150)}...`,
          metadata: { 
            prompt: message.prompt,  // Store FULL prompt
            provider: message.provider,
            model: message.model,
            strategy: (message as any).strategy  // Parse strategy if present
          },
        };
        
        console.log('[MONITOR] Parsed log:', requestLog);
        addLog(requestLog);
        console.log('[MONITOR]  llm_request log added');
        break;

      case 'llm_response':
        console.log('[MONITOR] Processing llm_response');
        console.log('[MONITOR] Role:', message.role, 'Response length:', message.response?.length);
        
        const responseLog = {
          timestamp,
          type: 'llm_response' as const,
          role: message.role,
          provider: message.provider,
          model: message.model,
          content: `${message.role?.toUpperCase()} Response (${message.latency_ms?.toFixed(0)}ms, ${message.tokens || 0} tokens): ${message.response?.slice(0, 150)}...`,
          metadata: { 
            response: message.response,  // Store FULL response
            latency_ms: message.latency_ms, 
            tokens: message.tokens,
            provider: message.provider,
            model: message.model,
            strategy: (message as any).strategy  // Parse strategy if present
          },
        };
        
        console.log('[MONITOR] Parsed log:', responseLog);
        addLog(responseLog);
        console.log('[MONITOR]  llm_response log added');
        break;

      case 'llm_error':
        addLog({
          timestamp,
          type: 'error',
          role: message.role,
          provider: message.provider,
          model: message.model,
          content: `Error from ${message.role}: ${message.error_message}`,
        });
        break;

      case 'attack_mutation':
        addLog({
          timestamp,
          type: 'attack',
          content: `Attack mutation (${message.strategy_used}): ${message.mutated_prompt?.slice(0, 150)}...`,
          metadata: { 
            strategy: message.strategy_used,
            original_prompt: message.original_prompt,
            mutated_prompt: message.mutated_prompt
          },
        });
        break;

      case 'target_response':
        addLog({
          timestamp,
          type: 'target',
          content: `Target response (${message.latency_ms?.toFixed(0)}ms): ${message.response?.slice(0, 200)}...`,
          metadata: { response: message.response, latency_ms: message.latency_ms },
        });
        break;

      case 'judge_evaluation':
        console.log('[MONITOR] Processing judge_evaluation');
        console.log('[MONITOR] Score:', message.judge_score, 'Success:', message.success);
        
        const judgeLog = {
          timestamp,
          type: 'judge' as const,
          content: `Judge Score: ${message.judge_score?.toFixed(2)}/10 | ${message.success ? 'JAILBREAK' : 'BLOCKED'}`,
          metadata: { 
            score: message.judge_score, 
            success: message.success, 
            reasoning: message.reasoning,  // Store FULL reasoning
            sub_scores: message.sub_scores,
            confidence: message.confidence,
            latency_ms: message.latency_ms,
            token_breakdown: message.token_breakdown,  // Comment 3: Store token_breakdown
            strategy: (message as any).strategy  // Parse strategy if present
          },
        };
        
        console.log('[MONITOR] Parsed log:', judgeLog);
        addLog(judgeLog);
        console.log('[MONITOR]  judge_evaluation log added');
        break;

      case 'iteration_complete':
        addLog({
          timestamp,
          type: 'info',
          content: `Iteration ${message.iteration} complete: Score ${message.judge_score?.toFixed(2)} (${message.success ? 'SUCCESS' : 'BLOCKED'})`,
        });
        // Update task status
        setTasks((prev) =>
          prev.map((t) =>
            t.id === `iter-${message.iteration}`
              ? { ...t, status: 'completed', completedAt: timestamp }
              : t
          )
        );
        // Add to iterations
        if (message.iteration !== undefined && message.judge_score !== undefined) {
          setIterations((prev) => [
            ...prev,
            {
              iteration_number: message.iteration!,
              strategy: message.strategy_used || 'unknown',
              prompt: '', // Will be filled from detailed data
              response: '',
              judge_score: message.judge_score!,
              success: message.success || false,
              latency_ms: message.latency_breakdown?.total_ms || 0,
              timestamp,
              latency_breakdown: message.latency_breakdown,
              token_breakdown: message.token_breakdown,
            },
          ]);
          if (message.success) {
            setSuccessfulIterations((prev) => prev + 1);
          }
        }
        break;

      case 'vulnerability_found':
        addLog({
          timestamp,
          type: 'error',  // Keep as 'error' for consistency
          content: `VULNERABILITY FOUND: ${(message as any).title || 'Jailbreak Successful'} (Severity: ${(message as any).severity || 'high'})`,
          metadata: {
            vulnerability_id: (message as any).vulnerability_id,
            severity: (message as any).severity,
            iteration: message.iteration,
            strategy: (message as any).attack_strategy || (message as any).strategy,
            judge_score: (message as any).judge_score,
            successful_prompt: (message as any).successful_prompt,
            target_response: (message as any).target_response,
            description: (message as any).description,
            title: (message as any).title,
          }
        });
        setVulnerabilitiesFound((prev) => prev + 1);
        break;

      case 'experiment_complete':
        addLog({
          timestamp,
          type: 'info',
          content: `Experiment complete: ${message.status} | ${message.vulnerabilities_found || 0} vulnerabilities | ${((message.success_rate || 0) * 100).toFixed(1)}% success rate`,
        });
        
        // Update backend status (hook will determine display status)
        setBackendStatus(message.status as ExperimentStatus || ExperimentStatus.COMPLETED);
        
        // Update vulnerabilities count from message
        if (message.vulnerabilities_found !== undefined) {
          setVulnerabilitiesFound(message.vulnerabilities_found);
        }
        break;

      case 'error':
        addLog({
          timestamp,
          type: 'error',
          content: `Error: ${message.error_message}`,
        });
        break;

      case 'task_queued':
      case 'task_started':
      case 'task_running':
      case 'task_completed':
      case 'task_failed':
        setTasks((prev) => {
          const existing = prev.find((t) => t.id === message.task_id);
          if (existing) {
            return prev.map((t) =>
              t.id === message.task_id
                ? { 
                    ...t, 
                    status: message.status as TaskQueueItem['status'],
                    // Update timestamps based on status
                    ...(message.status === 'running' && { startedAt: message.timestamp }),
                    ...(message.status === 'completed' && { completedAt: message.timestamp }),
                    ...(message.status === 'failed' && { completedAt: message.timestamp }),
                    // Comment 4: Update queue position if provided
                    ...(message.queue_position !== undefined && { queuePosition: message.queue_position })
                  }
                : t
            );
          }
          return [
            ...prev,
            {
              id: message.task_id || generateLogId(),
              name: message.task_name || 'Unknown Task',
              status: message.status as TaskQueueItem['status'] || 'queued',
              dependencies: message.dependencies || [],  // Phase 6
              queuePosition: message.queue_position,  // Comment 4: Persist queue position
            },
          ];
        });
        break;

      case 'strategy_selection':
        // Track strategy usage (Phase 3)
        if (message.strategy) {
          setUsedStrategies((prev) => ({
            ...prev,
            [message.strategy!]: (prev[message.strategy!] || 0) + 1,
          }));
        }
        if (message.available_strategies) {
          setSelectedStrategies(message.available_strategies);
        }
        addLog({
          timestamp,
          type: 'info',
          content: `Strategy Selection (Iteration ${message.iteration}): ${message.strategy} | Reasoning: ${message.reasoning}`,
          metadata: {
            strategy: message.strategy,
            reasoning: message.reasoning,
            preferred_categories: message.preferred_categories,
            filtered_count: message.filtered_count,
            available_strategies: message.available_strategies,
          },
        });
        break;

      case 'failure_analysis':  // Comment 2: Handle failure_analysis messages
        const analysis: FailureAnalysis = {
          failure_reason: message.failure_reason || 'Unknown',
          iterations_executed: message.iterations_executed || 0,
          max_iterations: message.max_iterations || 0,
          best_score: message.best_score || 0,
          best_iteration: message.best_iteration || 0,
          best_strategy: message.best_strategy || 'unknown',
          threshold_gap: message.threshold_gap || 0,
          success_threshold: experiment?.success_threshold || 7.0,
          strategy_performance: message.strategy_performance || {},
          iteration_breakdown: message.iteration_breakdown || [],
          recommendations: message.recommendations || []
        };
        setFailureAnalysis(analysis);
        setShowFailureModal(true);
        addLog({
          timestamp,
          type: 'error',
          content: `Experiment Failed: ${message.failure_reason || 'Unknown reason'}`
        });
        break;

      case 'code_flow':
        console.log('[ExperimentMonitor] Code Flow Event received:', {
          event_type: message.event_type,
          function_name: message.function_name,
          description: message.description,
          iteration: message.iteration
        });
        
        // Add to code-flow events
        setCodeFlowEvents((prev) => [
          ...prev.slice(-99),  // Keep last 100 events
          {
            id: generateLogId(),
            timestamp,
            event_type: message.event_type as CodeFlowEvent['event_type'],
            iteration: message.iteration,
            strategy: message.strategy,
            reasoning: message.reasoning,
            previous_score: message.previous_score,
            threshold: message.threshold,
            original_prompt: message.original_prompt,
            mutated_prompt: message.mutated_prompt,
            latency_ms: message.latency_ms,
            overall_score: message.overall_score,
            all_scores: message.all_scores,
            target_response: message.target_response,
            decision_type: message.decision_type,
            condition: message.condition,
            decision_result: message.decision_result as boolean | undefined,
            description: message.description,
            // Function call fields
            function_name: message.function_name,
            parameters: message.parameters,
            result: message.result,
          },
        ]);
        
        // Also add to logs for visibility
        addLog({
          timestamp,
          type: 'info',
          content: `Code Flow: ${message.event_type?.replace(/_/g, ' ')} ${message.description || ''}`,
        });
        break;

      case 'pong':
        // WebSocket keepalive - no action needed, just acknowledge
        break;

      default:
        console.log('[MONITOR] ️ Unknown message type:', message.type);
    }
    
    console.log('[MONITOR] ========== handleMessage COMPLETE ==========');
  }, [addLog]);

  // Load stored verbosity level when experimentId changes
  useEffect(() => {
    if (experimentId) {
      const storedVerbosity = getStoredVerbosity(experimentId);
      setVerbosity(storedVerbosity);
      console.log(`[ExperimentMonitor] Loaded verbosity level ${storedVerbosity} for experiment ${experimentId}`);
    }
  }, [experimentId]);

  // Fetch experiment details AND historical logs
  useEffect(() => {
    if (!experimentId) return;

    const fetchExperiment = async () => {
      try {
        const data = await apiClient.getExperiment(experimentId);
        setExperiment(data);
        setTotalIterations(data.max_iterations);
        setBackendStatus(data.status as ExperimentStatus);  // Use backendStatus
        
        // Load selected strategies from experiment (strategies is already an array of strings)
        if (data.strategies && Array.isArray(data.strategies)) {
          setSelectedStrategies(data.strategies);
        }
      } catch (error) {
        console.error('Failed to fetch experiment:', error);
      }
    };

    const fetchHistoricalLogs = async () => {
      try {
        const logsData = await apiClient.getExperimentLogs(experimentId);
        if (logsData && logsData.entries) {
          // Convert audit log entries to LiveLogEntry format
          const historicalLogs: LiveLogEntry[] = [];
          const historicalCodeFlowEvents: CodeFlowEvent[] = [];
          
          logsData.entries.forEach((entry: any, index: number) => {
            // AuditLogEntry structure from backend:
            // timestamp, event_type, experiment_id, iteration_number, model_attacker, model_target,
            // strategy, prompt_hash, success_score, latency_ms, tokens_used, error, metadata
            
            // Check if this is a code-flow event (strategy_transition or code_flow)
            if (entry.event_type === 'code_flow' || entry.event_type === 'strategy_transition') {
              historicalCodeFlowEvents.push({
                id: `historical-cf-${entry.timestamp}-${index}`,
                timestamp: entry.timestamp,
                event_type: entry.event_type as CodeFlowEvent['event_type'],
                iteration: entry.iteration_number,
                strategy: entry.strategy || entry.metadata?.to_strategy,
                reasoning: entry.metadata?.reason || entry.metadata?.reasoning,
                previous_score: entry.metadata?.judge_score,
                threshold: entry.metadata?.threshold_used,
                function_name: entry.metadata?.function_name,
                parameters: entry.metadata?.parameters,
                result: entry.metadata?.result,
              });
            } else {
              // Regular log entry - build meaningful content from available fields
              let content = '';
              const eventType = entry.event_type || 'info';
              
              // Build human-readable content based on event type
              switch (eventType) {
                case 'attack_attempt':
                  content = `Attack attempt using ${entry.strategy || 'unknown'} strategy`;
                  if (entry.metadata?.input_prompt) {
                    content += `: "${entry.metadata.input_prompt.substring(0, 100)}..."`;
                  }
                  break;
                case 'mutation':
                  content = `Mutation: ${entry.strategy || 'unknown'} strategy`;
                  if (entry.metadata?.output_prompt) {
                    content += ` → "${entry.metadata.output_prompt.substring(0, 100)}..."`;
                  }
                  break;
                case 'judge_evaluation':
                  content = `Judge score: ${entry.success_score ?? 'N/A'}/10`;
                  if (entry.metadata?.reasoning) {
                    content += ` - ${entry.metadata.reasoning.substring(0, 150)}...`;
                  }
                  break;
                case 'error':
                  content = entry.error || 'Unknown error';
                  break;
                case 'target_response':
                  content = `Target response (${entry.latency_ms}ms)`;
                  if (entry.metadata?.response) {
                    content += `: "${entry.metadata.response.substring(0, 100)}..."`;
                  }
                  break;
                default:
                  // Fallback: try to extract meaningful info from metadata
                  if (entry.error) {
                    content = entry.error;
                  } else if (entry.metadata?.prompt) {
                    content = `Prompt: "${entry.metadata.prompt.substring(0, 100)}..."`;
                  } else if (entry.metadata?.response) {
                    content = `Response: "${entry.metadata.response.substring(0, 100)}..."`;
                  } else if (Object.keys(entry.metadata || {}).length > 0) {
                    // Show first few metadata keys
                    const keys = Object.keys(entry.metadata).slice(0, 3);
                    content = `${eventType}: ${keys.join(', ')}`;
                  } else {
                    content = `${eventType} event`;
                  }
              }
              
              historicalLogs.push({
                id: `historical-${entry.timestamp}-${index}`,
                timestamp: entry.timestamp,
                type: eventType,
                content: content,
                metadata: {
                  ...entry.metadata,
                  strategy: entry.strategy,
                  iteration: entry.iteration_number,
                  latency_ms: entry.latency_ms,
                  tokens_used: entry.tokens_used,
                  success_score: entry.success_score,
                  error: entry.error,
                },
                role: entry.metadata?.role || (eventType === 'attack_attempt' ? 'attacker' : eventType === 'judge_evaluation' ? 'judge' : 'target'),
                provider: entry.metadata?.provider || entry.model_attacker?.split('/')[0] || entry.model_target?.split('/')[0],
                model: entry.metadata?.model || entry.model_attacker || entry.model_target,
              });
            }
          });
          
          // Set historical logs and code-flow events
          setLogs(historicalLogs);
          setCodeFlowEvents(historicalCodeFlowEvents);
          console.log(`Loaded ${historicalLogs.length} historical log entries and ${historicalCodeFlowEvents.length} code-flow events`);
        }
      } catch (error) {
        console.error('Failed to fetch historical logs:', error);
      }
    };

    fetchExperiment();
    fetchHistoricalLogs();  // Load ALL historical logs from database
  }, [experimentId]);

  // Connect to WebSocket (only if experiment is running or pending)
  useEffect(() => {
    if (!experimentId) return;
    
    // Only connect if experiment is running or pending (for live updates)
    // For completed/failed experiments, we rely on historical data from API
    if (status === 'running' || status === 'pending' || !status) {
      wsClient.connect(experimentId, verbosity);  // Pass verbosity
      const unsubscribe = wsClient.onMessage(handleMessage);

      return () => {
        unsubscribe();
        wsClient.disconnect();
      };
    }
  }, [experimentId, handleMessage, status]);  // Re-connect if status changes to running

  // Poll for status updates (fallback)
  useEffect(() => {
    if (!experimentId) return;

    const pollStatus = async () => {
      try {
        const [statusData, statisticsData] = await Promise.all([
          apiClient.getScanStatus(experimentId).catch(err => {
            console.error('Failed to poll status:', err);
            return null;
          }),
          apiClient.getExperimentStatistics(experimentId).catch(err => {
            console.error('Failed to poll statistics:', err);
            return null;
          })
        ]);
        
        if (statusData) {
          // Update iteration counts (hook will calculate progress)
          setCurrentIteration(Math.min(statusData.current_iteration, statusData.total_iterations));
          setTotalIterations(statusData.total_iterations);
          setElapsedSeconds(statusData.elapsed_time_seconds);
          
          // Update backend status (hook will determine display status)
          setBackendStatus(statusData.status as ExperimentStatus);
          
          if (statisticsData) {
            setSuccessfulIterations(statisticsData.successful_iterations);
            setVulnerabilitiesFound(statisticsData.vulnerabilities_found);
          }
        }
      } catch (error) {
        console.error('Failed to poll status:', error);
      }
    };

    // Initial poll
    pollStatus();

    // Poll every 5 seconds as fallback
    const interval = setInterval(pollStatus, 5000);

    return () => clearInterval(interval);
  }, [experimentId]);

  // Reconstruct logs and tasks from iterations
  const reconstructLogsFromIterations = useCallback((iterData: any[]) => {
    const reconstructedLogs: LiveLogEntry[] = [];
    const reconstructedTasks: TaskQueueItem[] = [];

    iterData.forEach((iter: any) => {
      const timestamp = iter.timestamp || new Date().toISOString();
      const iterationNum = iter.iteration_number || 0;

      // Add task for mutation
      if (iter.mutated_prompt) {
        reconstructedTasks.push({
          id: `task-mutate-${iterationNum}`,
          name: `Iteration ${iterationNum}: Mutate Prompt`,
          status: 'completed',
          iteration: iterationNum,
          strategy: iter.strategy_used || 'unknown'
        });

        // Add log entry for mutation
        reconstructedLogs.push({
          id: `log-mutate-${iterationNum}`,
          timestamp,
          type: 'attack',
          role: 'attacker',
          content: `Iteration ${iterationNum}: Prompt mutation using ${iter.strategy_used || 'unknown'}`,
          metadata: {
            prompt: iter.mutated_prompt,
            strategy: iter.strategy_used,
            iteration: iterationNum
          }
        });
      }

      // Add task for target LLM query
      if (iter.target_response) {
        reconstructedTasks.push({
          id: `task-query-${iterationNum}`,
          name: `Iteration ${iterationNum}: Query Target LLM`,
          status: 'completed',
          iteration: iterationNum,
          strategy: iter.strategy_used || 'unknown'
        });

        // Add log entry for target response
        reconstructedLogs.push({
          id: `log-target-${iterationNum}`,
          timestamp,
          type: 'llm_response',
          role: 'target',
          content: iter.target_response.substring(0, 200) + (iter.target_response.length > 200 ? '...' : ''),
          metadata: {
            response: iter.target_response,
            prompt: iter.mutated_prompt || iter.original_prompt,
            latency_ms: iter.latency_ms,
            tokens: iter.tokens_used?.response || 0,
            iteration: iterationNum
          }
        });
      }

      // Add task for judge evaluation
      if (iter.judge_score !== undefined) {
        reconstructedTasks.push({
          id: `task-judge-${iterationNum}`,
          name: `Iteration ${iterationNum}: Judge Evaluation`,
          status: 'completed',
          iteration: iterationNum,
          strategy: iter.strategy_used || 'unknown'
        });

        // Add log entry for judge evaluation
        reconstructedLogs.push({
          id: `log-judge-${iterationNum}`,
          timestamp,
          type: 'judge',
          role: 'judge',
          content: `Judge Score: ${iter.judge_score.toFixed(2)} | Success: ${iter.success ? 'Yes' : 'No'}`,
          metadata: {
            score: iter.judge_score,
            success: iter.success,
            reasoning: iter.judge_reasoning,
            iteration: iterationNum
          }
        });
        
        // Check if this iteration resulted in a vulnerability
        if (iter.success && iter.judge_score >= 7.0) {  // Assuming threshold is 7.0
          reconstructedLogs.push({
            id: `log-vulnerability-${iterationNum}`,
            timestamp,
            type: 'error',  // Vulnerabilities use 'error' type
            content: `VULNERABILITY FOUND in Iteration ${iterationNum}: ${iter.strategy_used || 'unknown'} attack succeeded (Score: ${iter.judge_score.toFixed(2)})`,
            metadata: {
              vulnerability_id: iter.vulnerability_id || `vuln-iter-${iterationNum}`,  // Use actual ID if available
              severity: iter.severity || 'high',
              iteration: iterationNum,
              strategy: iter.strategy_used,
              judge_score: iter.judge_score,
              successful_prompt: iter.mutated_prompt,
              target_response: iter.target_response,
            }
          });
        }
      }

      // Add iteration complete log
      reconstructedLogs.push({
        id: `log-iteration-complete-${iterationNum}`,
        timestamp,
        type: 'info',
        content: `Iteration ${iterationNum} complete: ${iter.success ? 'SUCCESS' : 'FAILED'} (Score: ${iter.judge_score?.toFixed(2) || 'N/A'})`,
        metadata: {
          iteration: iterationNum,
          success: iter.success,
          score: iter.judge_score
        }
      });
    });

    return { logs: reconstructedLogs, tasks: reconstructedTasks };
  }, []);

  // Fetch iterations and vulnerabilities - on mount, when iteration changes, and when status changes to completed/failed
  useEffect(() => {
    if (!experimentId) return;

    const fetchData = async () => {
      try {
        console.log('Fetching iterations for experiment:', experimentId);
        const [iterationsData, vulnerabilitiesData] = await Promise.all([
          apiClient.getExperimentIterations(experimentId).catch(err => {
            console.error('Failed to fetch iterations:', err);
            return { iterations: [], total: 0 };
          }),
          apiClient.getVulnerabilities({ experiment_id: experimentId }).catch(err => {
            console.error('Failed to fetch vulnerabilities:', err);
            return { vulnerabilities: [], total: 0 };
          })
        ]);
        
        const iterData = iterationsData.iterations || [];
        console.log('Received iterations:', iterData.length, iterData);
        
        // Set iterations
        setIterations(
          iterData.map((iter: any) => ({
            iteration_number: iter.iteration_number,
            strategy: iter.strategy_used || 'unknown',
            prompt: iter.mutated_prompt || iter.original_prompt || '(Prompt nicht verfügbar)',
            response: iter.target_response || '(Response nicht verfügbar)',
            judge_score: iter.judge_score || 0,
            judge_reasoning: iter.judge_reasoning || '(Reasoning nicht verfügbar)',
            success: iter.success || false,
            latency_ms: iter.latency_ms || 0,
            timestamp: iter.timestamp || new Date().toISOString(),
            // Additional fields for detailed view
            original_prompt: iter.original_prompt,
            target_model: iter.target_model,
            attacker_model: iter.attacker_model,
            tokens_used: iter.tokens_used,
            // Breakdown fields
            latency_breakdown: iter.latency_breakdown,
            token_breakdown: iter.token_breakdown,
            sub_scores: iter.sub_scores || {
              jailbreak_success: iter.judge_score || 0,
              harmful_content: 0,
              hallucination: 0,
              bias: 0,
              logical_consistency: 0,
              sycophancy: 0,
              policy_violation: 0
            },
            confidence: iter.confidence
          }))
        );
        
        // Reconstruct logs and tasks from iterations (for historical data)
        if (iterData.length > 0) {
          const { logs: reconstructedLogs, tasks: reconstructedTasks } = reconstructLogsFromIterations(iterData);
          
          // Only set logs/tasks if they're empty (don't overwrite live WebSocket data)
          setLogs((prev) => {
            // If we have live logs, merge with reconstructed (avoid duplicates)
            if (prev.length > 0) {
              const existingIds = new Set(prev.map(l => l.id));
              const newLogs = reconstructedLogs.filter(l => !existingIds.has(l.id));
              return [...prev, ...newLogs].slice(-500); // Keep last 500
            }
            // If no live logs, use reconstructed
            return reconstructedLogs;
          });
          
          setTasks((prev) => {
            // If we have live tasks, merge with reconstructed (avoid duplicates)
            if (prev.length > 0) {
              const existingIds = new Set(prev.map(t => t.id));
              const newTasks = reconstructedTasks.filter(t => !existingIds.has(t.id));
              return [...prev, ...newTasks];
            }
            // If no live tasks, use reconstructed
            return reconstructedTasks;
          });
          
          // Reconstruct usedStrategies from iterations (count strategy usage)
          const strategyCounts: Record<string, number> = {};
          iterData.forEach((iter: any) => {
            const strategy = iter.strategy_used || iter.strategy;
            if (strategy && strategy !== 'unknown') {
              strategyCounts[strategy] = (strategyCounts[strategy] || 0) + 1;
            }
          });
          
          // Merge with existing usedStrategies (preserve live WebSocket data)
          setUsedStrategies((prev) => {
            // If we have live data, merge with reconstructed
            if (Object.keys(prev).length > 0) {
              const merged = { ...prev };
              Object.entries(strategyCounts).forEach(([strategy, count]) => {
                merged[strategy] = (merged[strategy] || 0) + count;
              });
              return merged;
            }
            // If no live data, use reconstructed
            return strategyCounts;
          });
        }
        
        const successfulCount = iterData.filter((i: any) => i.success).length;
        setSuccessfulIterations(successfulCount);
        
        // Update vulnerabilities count from API
        const vulnCount = vulnerabilitiesData.vulnerabilities?.length || 0;
        setVulnerabilitiesFound(vulnCount);
        console.log('Vulnerabilities found:', vulnCount);
        
        // Convert vulnerabilities to LiveLogEntry format
        if (vulnerabilitiesData.vulnerabilities && vulnerabilitiesData.vulnerabilities.length > 0) {
          const vulnerabilityLogs: LiveLogEntry[] = vulnerabilitiesData.vulnerabilities.map((vuln: VulnerabilityFinding) => ({
            id: `vuln-${vuln.vulnerability_id}`,
            timestamp: vuln.discovered_at,
            type: 'error' as const,  // Vulnerabilities use 'error' type
            content: `VULNERABILITY FOUND: ${vuln.title} (Severity: ${vuln.severity})`,
            metadata: {
              vulnerability_id: vuln.vulnerability_id,
              severity: vuln.severity,
              iteration: vuln.iteration_number,
              strategy: vuln.attack_strategy,
              judge_score: vuln.judge_score,
              successful_prompt: vuln.successful_prompt,
              target_response: vuln.target_response,
              description: vuln.description,
              mitigation_suggestions: vuln.mitigation_suggestions,
              cve_references: vuln.cve_references,
            }
          }));
          
          // Merge vulnerability logs with existing logs - API logs replace existing ones with same vulnerability_id
          setLogs((prev) => {
            // Get set of API vulnerability IDs (these have richer details)
            const apiVulnIds = new Set(
              vulnerabilityLogs.map(vl => vl.metadata!.vulnerability_id as string)
            );
            
            // Remove existing logs that match API vulnerability IDs (to be replaced with richer API data)
            const filteredPrev = prev.filter(
              l => !l.metadata?.vulnerability_id || !apiVulnIds.has(l.metadata.vulnerability_id as string)
            );
            
            // Add all API vulnerability logs (they have richer fields like title, description, mitigation_suggestions)
            return [...filteredPrev, ...vulnerabilityLogs];
          });
          
          console.log(`Added ${vulnerabilityLogs.length} vulnerability log entries (replaced existing with richer API data)`);
        }
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    };

    // Fetch immediately on mount - ALWAYS, not just when running
    fetchData();
    
    // Also poll every 3 seconds while running
    let interval: ReturnType<typeof setInterval> | null = null;
    if (status === 'running') {
      interval = setInterval(fetchData, 3000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [experimentId, status, currentIteration, reconstructLogsFromIterations]);

  if (!experimentId) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-slate-400">No experiment ID provided</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              to="/experiments"
              className="text-slate-400 hover:text-slate-200 transition-colors"
            >
              ← Back
            </Link>
            <h1 className="text-xl font-bold">
              Live Monitor
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(`/experiments/${experimentId}`)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm transition-colors"
            >
              View Details
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6 space-y-6">
        {/* Progress Overview */}
        <ProgressOverview
          experimentId={experimentId}
          experimentName={experiment?.name || 'Loading...'}
          status={status}
          currentIteration={currentIteration}
          totalIterations={totalIterations}
          progressPercent={progressPercent}
          elapsedSeconds={elapsedSeconds}
          successfulIterations={successfulIterations}
          vulnerabilitiesFound={vulnerabilitiesFound}
          isConnected={isConnected}
          successThreshold={experiment?.success_threshold || 7.0}
        />

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
          <button
            onClick={() => setActiveTab('logs')}
            className={`px-4 py-2 rounded-t-lg transition-colors ${
              activeTab === 'logs'
                ? 'bg-slate-800 text-cyan-400 border-b-2 border-cyan-400'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Live Logs
          </button>
          <button
            onClick={() => setActiveTab('iterations')}
            className={`px-4 py-2 rounded-t-lg transition-colors ${
              activeTab === 'iterations'
                ? 'bg-slate-800 text-cyan-400 border-b-2 border-cyan-400'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Iterations ({iterations.length})
          </button>
          <button
            onClick={() => setActiveTab('tasks')}
            className={`px-4 py-2 rounded-t-lg transition-colors ${
              activeTab === 'tasks'
                ? 'bg-slate-800 text-cyan-400 border-b-2 border-cyan-400'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Task Queue
          </button>
          <button
            onClick={() => setActiveTab('code-flow')}
            className={`px-4 py-2 rounded-t-lg transition-colors ${
              activeTab === 'code-flow'
                ? 'bg-slate-800 text-cyan-400 border-b-2 border-cyan-400'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Code Flow ({codeFlowEvents.length})
          </button>
          <button
            onClick={() => setActiveTab('strategy-usage')}
            className={`px-4 py-2 rounded-t-lg transition-colors ${
              activeTab === 'strategy-usage'
                ? 'bg-slate-800 text-cyan-400 border-b-2 border-cyan-400'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Strategy Usage
          </button>

        </div>

        {/* Verbosity Selector */}
        <VerbositySelector 
          value={verbosity}
          onChange={handleVerbosityChange}
          isConnected={isConnected}
        />

        {/* Content Panels */}
        <div className="h-[calc(100vh-400px)] min-h-[400px]">
          {activeTab === 'logs' && (
            <LiveLogPanel 
              logs={logs} 
              tasks={tasks}
              codeFlowEvents={codeFlowEvents}
            />
          )}
          {activeTab === 'iterations' && (
            <IterationResultsPanel
              iterations={iterations}
              successThreshold={experiment?.success_threshold || 7.0}
            />
          )}
          {activeTab === 'tasks' && (
            <TaskQueuePanel tasks={tasks} />
          )}
        {activeTab === 'code-flow' && (
          <CodeFlowPanel events={codeFlowEvents} />
        )}

        {activeTab === 'strategy-usage' && (
          <StrategyUsagePanel
            selectedStrategies={selectedStrategies}
            usedStrategies={usedStrategies}
          />
        )}
        </div>
      </main>

      {/* Failure Analysis Modal */}
      {showFailureModal && failureAnalysis && (
        <div 
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          onClick={() => setShowFailureModal(false)}
        >
          <div 
            className="bg-slate-900 rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden m-4 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <FailureAnalysisPanel
              analysis={failureAnalysis}
              onClose={() => setShowFailureModal(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ExperimentMonitor;
