/**
 * TypeScript type definitions for CEREBRO-RED v2 API.
 * 
 * These types mirror the Pydantic models from the backend to ensure
 * type safety across the frontend-backend boundary.
 */

// ============================================================================
// Enums (exact match with backend)
// ============================================================================

export enum AttackStrategyType {
  // === OBFUSCATION TECHNIQUES ===
  OBFUSCATION_BASE64 = "obfuscation_base64",
  OBFUSCATION_LEETSPEAK = "obfuscation_leetspeak",
  OBFUSCATION_ROT13 = "obfuscation_rot13",
  OBFUSCATION_ASCII_ART = "obfuscation_ascii_art",
  OBFUSCATION_UNICODE = "obfuscation_unicode",
  OBFUSCATION_TOKEN_SMUGGLING = "obfuscation_token_smuggling",
  OBFUSCATION_MORSE = "obfuscation_morse",
  OBFUSCATION_BINARY = "obfuscation_binary",

  // === JAILBREAK TECHNIQUES (2024-2025) ===
  JAILBREAK_DAN = "jailbreak_dan",
  JAILBREAK_AIM = "jailbreak_aim",
  JAILBREAK_STAN = "jailbreak_stan",
  JAILBREAK_DUDE = "jailbreak_dude",
  JAILBREAK_DEVELOPER_MODE = "jailbreak_developer_mode",

  // === ADVANCED MULTI-TURN ATTACKS ===
  CRESCENDO_ATTACK = "crescendo_attack",
  MANY_SHOT_JAILBREAK = "many_shot_jailbreak",
  SKELETON_KEY = "skeleton_key",

  // === PROMPT INJECTION (OWASP LLM01) ===
  DIRECT_INJECTION = "direct_injection",
  INDIRECT_INJECTION = "indirect_injection",
  PAYLOAD_SPLITTING = "payload_splitting",
  VIRTUALIZATION = "virtualization",

  // === CONTEXT MANIPULATION ===
  CONTEXT_FLOODING = "context_flooding",
  CONTEXT_IGNORING = "context_ignoring",
  CONVERSATION_RESET = "conversation_reset",

  // === SOCIAL ENGINEERING ===
  ROLEPLAY_INJECTION = "roleplay_injection",
  AUTHORITY_MANIPULATION = "authority_manipulation",
  URGENCY_EXPLOITATION = "urgency_exploitation",
  EMOTIONAL_MANIPULATION = "emotional_manipulation",

  // === SEMANTIC ATTACKS ===
  REPHRASE_SEMANTIC = "rephrase_semantic",
  SYCOPHANCY = "sycophancy",
  LINGUISTIC_EVASION = "linguistic_evasion",
  TRANSLATION_ATTACK = "translation_attack",

  // === SYSTEM PROMPT ATTACKS (OWASP LLM07) ===
  SYSTEM_PROMPT_EXTRACTION = "system_prompt_extraction",
  SYSTEM_PROMPT_OVERRIDE = "system_prompt_override",

  // === RAG ATTACKS ===
  RAG_POISONING = "rag_poisoning",
  RAG_BYPASS = "rag_bypass",
  ECHOLEAK = "echoleak",

  // === ADVERSARIAL ML ===
  ADVERSARIAL_SUFFIX = "adversarial_suffix",
  GRADIENT_BASED = "gradient_based",

  // === BIAS AND HALLUCINATION PROBES ===
  BIAS_PROBE = "bias_probe",
  HALLUCINATION_PROBE = "hallucination_probe",
  MISINFORMATION_INJECTION = "misinformation_injection",

  // === MCP (Model Context Protocol) ATTACKS ===
  MCP_TOOL_INJECTION = "mcp_tool_injection",
  MCP_CONTEXT_POISONING = "mcp_context_poisoning",

  // === ADVANCED RESEARCH PRE-JAILBREAK ===
  RESEARCH_PRE_JAILBREAK = "research_pre_jailbreak"
}

export enum VulnerabilitySeverity {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical"
}

export enum ExperimentStatus {
  PENDING = "pending",
  RUNNING = "running",
  PAUSED = "paused",
  COMPLETED = "completed",
  FAILED = "failed"
}

export enum LLMProvider {
  OLLAMA = "ollama",
  AZURE = "azure",
  OPENAI = "openai"
}

// ============================================================================
// Interfaces (based on backend Pydantic models)
// ============================================================================

export interface ExperimentConfig {
  experiment_id?: string;
  name: string;
  description?: string;
  target_model_provider: LLMProvider;
  target_model_name: string;
  attacker_model_provider: LLMProvider;
  attacker_model_name: string;
  judge_model_provider: LLMProvider;
  judge_model_name: string;
  initial_prompts: string[];
  strategies: AttackStrategyType[];
  max_iterations: number;
  max_concurrent_attacks: number;
  success_threshold: number;
  timeout_seconds: number;
  created_at?: string;
  metadata?: Record<string, unknown>;
}

export interface ExperimentResponse {
  experiment_id: string;
  name: string;
  description?: string;
  target_model_provider: string;
  target_model_name: string;
  attacker_model_provider: string;
  attacker_model_name: string;
  judge_model_provider: string;
  judge_model_name: string;
  initial_prompts: string[];
  strategies: string[];
  max_iterations: number;
  max_concurrent_attacks: number;
  success_threshold: number;
  timeout_seconds: number;
  status: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface ExperimentListResponse {
  items: ExperimentResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface AttackIteration {
  iteration_id: string;
  experiment_id: string;
  iteration_number: number;
  strategy_used: string;
  original_prompt: string;
  mutated_prompt: string;
  target_response: string;
  judge_score: number;
  judge_reasoning: string;
  success: boolean;
  latency_ms: number;
  timestamp: string;
  attacker_feedback?: string;
}

export interface VulnerabilityFinding {
  vulnerability_id: string;
  experiment_id: string;
  severity: VulnerabilitySeverity;
  title: string;
  description: string;
  successful_prompt: string;
  target_response: string;
  attack_strategy: AttackStrategyType;
  iteration_number: number;
  judge_score: number;
  reproducible: boolean;
  cve_references: string[];
  mitigation_suggestions: string[];
  discovered_at: string;
  metadata: Record<string, unknown>;
}

export interface ScanStatusResponse {
  experiment_id: string;
  status: string;
  current_iteration: number;
  total_iterations: number;
  progress_percent: number;
  elapsed_time_seconds: number;
  estimated_remaining_seconds?: number;
}

export interface ExperimentStatistics {
  experiment_id: string;
  status: string;
  total_iterations: number;
  successful_iterations: number;
  success_rate: number;
  vulnerabilities_found: number;
  strategy_distribution: Record<string, number>;
  severity_distribution: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  created_at: string;
}

export interface VulnerabilityStatistics {
  total_vulnerabilities: number;
  by_severity: Record<string, number>;
  by_strategy: Record<string, number>;
}

// ============================================================================
// Experiment Template Types
// ============================================================================

export interface ExperimentTemplate {
  template_id?: string;
  name: string;
  description?: string;
  config: ExperimentConfig;
  tags: string[];
  is_public: boolean;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
  usage_count?: number;
}

export interface ExperimentTemplateCreate {
  name: string;
  description?: string;
  config: ExperimentConfig;
  tags?: string[];
  is_public?: boolean;
  created_by?: string;
}

export interface ExperimentTemplateUpdate {
  name?: string;
  description?: string;
  config?: ExperimentConfig;
  tags?: string[];
  is_public?: boolean;
}

export interface ExperimentTemplateListResponse {
  items: ExperimentTemplate[];
  total: number;
  page: number;
  page_size: number;
}

// ============================================================================
// WebSocket Message Types
// ============================================================================

export type WSMessageType = 
  | 'connected' 
  | 'progress' 
  | 'iteration_complete' 
  | 'iteration_start'
  | 'vulnerability_found' 
  | 'experiment_complete' 
  | 'error' 
  | 'pong'
  // Live Monitoring Events
  | 'llm_request'
  | 'llm_response'
  | 'llm_error'
  | 'judge_evaluation'
  | 'attack_mutation'
  | 'target_response'
  | 'task_queued'
  | 'task_started'
  | 'task_running'  // Task running event (alias for task_started)
  | 'task_completed'
  | 'task_failed'  // Task failed event
  | 'code_flow'  // Code-flow events (verbosity level 3)
  | 'verbosity_updated'  // Verbosity level change confirmation
  | 'failure_analysis'  // Detailed failure analysis for failed experiments
  | 'strategy_selection';  // Detailed strategy selection event (Phase 3)

export interface WSMessage {
  type: WSMessageType;
  experiment_id?: string;
  message?: string;
  iteration?: number;
  total_iterations?: number;
  progress_percent?: number;
  current_strategy?: string;
  elapsed_time_seconds?: number;
  success?: boolean;
  judge_score?: number;
  strategy_used?: string;
  vulnerability_id?: string;
  severity?: string;
  status?: string;
  vulnerabilities_found?: number;
  success_rate?: number;
  error_message?: string;
  timestamp?: string;
  // LLM-specific fields
  provider?: string;
  model?: string;
  role?: 'attacker' | 'target' | 'judge';
  prompt?: string;
  response?: string;
  latency_ms?: number;
  tokens?: number;
  reasoning?: string;
  // Task queue fields
  task_id?: string;
  task_name?: string;
  queue_position?: number;
  dependencies?: string[];  // Phase 6: Task dependencies
  // Latency/token breakdown fields (when type === 'iteration_complete')
  latency_breakdown?: { mutation_ms: number; target_ms: number; judge_ms: number; total_ms: number };
  token_breakdown?: { attacker: number; target: number; judge: number; total: number };
  // Judge sub-scores (when type === 'judge_evaluation')
  sub_scores?: Record<string, number>;
  confidence?: number;
  // Code-flow fields (when type === 'code_flow')
  event_type?: string;
  function_name?: string;
  description?: string;
  parameters?: Record<string, unknown>;
  result?: unknown;
  previous_score?: number;
  threshold?: number;
  original_prompt?: string;
  mutated_prompt?: string;
  overall_score?: number;
  all_scores?: Record<string, number>;
  target_response?: string;
  decision_type?: string;
  condition?: string;
  decision_result?: boolean;  // Decision point result (separate from function result)
  // Strategy selection fields (when type === 'strategy_selection')
  strategy?: string;
  available_strategies?: string[];
  preferred_categories?: string[];
  filtered_count?: number;
  // Verbosity fields
  verbosity?: number;
  // Failure analysis fields (when type === 'failure_analysis')
  failure_reason?: string;
  iterations_executed?: number;
  max_iterations?: number;
  best_score?: number;
  best_iteration?: number;
  best_strategy?: string;
  threshold_gap?: number;
  success_threshold?: number;
  strategy_performance?: Record<string, { attempts: number; avg_score: number; success_rate: number }>;
  iteration_breakdown?: Array<{ iteration: number; strategy: string; score: number; success: boolean }>;
  recommendations?: string[];
}

// ============================================================================
// Live Monitor Types
// ============================================================================

export interface LiveLogEntry {
  id: string;
  timestamp: string;
  type: 'llm_request' | 'llm_response' | 'llm_error' | 'judge' | 'attack' | 'target' | 'error' | 'info' | 'task';
  role?: 'attacker' | 'target' | 'judge';
  provider?: string;
  model?: string;
  content: string;
  metadata?: {
    prompt?: string;           // Full prompt (not truncated)
    response?: string;         // Full response (not truncated)
    latency_ms?: number;
    tokens?: number;
    score?: number;
    success?: boolean;
    reasoning?: string;
    strategy?: string;
    error_message?: string;
    [key: string]: unknown;    // Allow additional metadata
  };
}

export interface TaskQueueItem {
  id: string;
  name: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  iteration?: number;
  strategy?: string;
  startedAt?: string;
  completedAt?: string;
  dependencies?: string[];  // Phase 6: Task IDs this task depends on
  queuePosition?: number;  // Comment 4: Position in queue
}

export interface IterationResult {
  iteration_number: number;
  strategy: string;
  prompt: string;
  response: string;
  judge_score: number;
  judge_reasoning?: string;
  success: boolean;
  latency_ms: number;
  timestamp: string;
  
  // Latency breakdown
  latency_breakdown?: {
    mutation_ms: number;
    target_ms: number;
    judge_ms: number;
    total_ms: number;
  };
  
  // Token breakdown
  token_breakdown?: {
    attacker: number;
    target: number;
    judge: number;
    total: number;
  };
  
  // Judge sub-scores (7 criteria)
  sub_scores?: {
    jailbreak_success: number;
    harmful_content: number;
    hallucination: number;
    bias: number;
    logical_consistency: number;
    sycophancy: number;
    policy_violation: number;
  };
  
  confidence?: number;
}

export interface CodeFlowEvent {
  id?: string;
  timestamp: string;
  event_type: 'strategy_selection' | 'mutation_start' | 'mutation_end' | 'judge_start' | 'judge_end' | 'decision_point' | 'function_call';
  iteration?: number;
  
  // Function call fields (for function_call event_type)
  function_name?: string;
  parameters?: Record<string, unknown>;
  result?: unknown;
  
  // Strategy selection fields
  strategy?: string;
  reasoning?: string;
  previous_score?: number;
  threshold?: number;
  
  // Mutation fields
  original_prompt?: string;
  mutated_prompt?: string;
  latency_ms?: number;
  
  // Judge fields
  overall_score?: number;
  all_scores?: Record<string, number>;
  target_response?: string;
  
  // Decision point fields
  decision_type?: string;
  condition?: string;
  decision_result?: boolean;
  description?: string;
}

export interface FailureAnalysis {
  failure_reason: string;
  iterations_executed: number;
  max_iterations: number;
  best_score: number;
  best_iteration: number;
  best_strategy: string;
  threshold_gap: number;
  success_threshold: number;
  strategy_performance: Record<string, {
    attempts: number;
    avg_score: number;
    success_rate: number;
  }>;
  iteration_breakdown: Array<{
    iteration: number;
    strategy: string;
    score: number;
    success: boolean;
  }>;
  recommendations: string[];
}

export interface LiveMonitorState {
  isConnected: boolean;
  logs: LiveLogEntry[];
  taskQueue: TaskQueueItem[];
  iterations: IterationResult[];
  currentIteration: number;
  totalIterations: number;
  progressPercent: number;
  elapsedSeconds: number;
  status: ExperimentStatus;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiResponse<T> {
  data: T;
}

export interface ApiError {
  error: string;
  type: string;
  path: string;
  detail?: string;
}

// ============================================================================
// Demo Mode Types
// ============================================================================

export interface DemoModeConfig {
  enabled: boolean;
  message?: string;
  features: {
    readOnly: boolean;
    mockData: boolean;
  };
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
  components: {
    database: string;
    llm_providers: Record<string, string>;
    telemetry: string;
    cors: string;
  };
  demo_mode?: boolean;
  timestamp: string;
}

