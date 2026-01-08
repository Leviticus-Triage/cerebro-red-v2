/**
 * Form type definitions for CEREBRO-RED v2.
 */

import { AttackStrategyType, LLMProvider } from './api';

export interface ExperimentFormData {
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
}

