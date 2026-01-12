# Copyright 2024-2026 Cerebro-Red v2 Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
backend/core/models.py
======================

Pydantic data models for CEREBRO-RED v2 implementing the PAIR algorithm
(Prompt Automatic Iterative Refinement) from arxiv.org/abs/2310.08419.

These models provide strict type validation and serialization for:
- Experiment configuration and lifecycle management
- Attack iteration tracking with full provenance
- Prompt mutation strategies and history
- LLM-as-a-Judge evaluation with Chain-of-Thought reasoning
- Vulnerability findings with severity classification

All models use Pydantic v2 with strict validation and are compatible
with SQLAlchemy ORM via `from_attributes=True` configuration.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator


# ============================================================================
# Core Enums
# ============================================================================

class AttackStrategyType(str, Enum):
    """
    Attack strategy types for prompt mutation.
    
    Based on OWASP Top 10 for LLM Applications 2025, Microsoft AI Red Team,
    NVIDIA garak, PyRIT, and latest research papers.
    """
    
    # === OBFUSCATION TECHNIQUES ===
    OBFUSCATION_BASE64 = "obfuscation_base64"
    OBFUSCATION_LEETSPEAK = "obfuscation_leetspeak"
    OBFUSCATION_ROT13 = "obfuscation_rot13"
    OBFUSCATION_ASCII_ART = "obfuscation_ascii_art"  # ASCII art encoding
    OBFUSCATION_UNICODE = "obfuscation_unicode"  # Unicode homoglyphs and confusables
    OBFUSCATION_TOKEN_SMUGGLING = "obfuscation_token_smuggling"  # Token boundary exploitation
    OBFUSCATION_MORSE = "obfuscation_morse"  # Morse code encoding
    OBFUSCATION_BINARY = "obfuscation_binary"  # Binary encoding
    
    # === JAILBREAK TECHNIQUES (2024-2025) ===
    JAILBREAK_DAN = "jailbreak_dan"  # Do Anything Now variants
    JAILBREAK_AIM = "jailbreak_aim"  # Always Intelligent and Machiavellian
    JAILBREAK_STAN = "jailbreak_stan"  # Strive To Avoid Norms
    JAILBREAK_DUDE = "jailbreak_dude"  # Do Anything Now variant
    JAILBREAK_DEVELOPER_MODE = "jailbreak_developer_mode"  # Developer mode bypass
    
    # === ADVANCED MULTI-TURN ATTACKS ===
    CRESCENDO_ATTACK = "crescendo_attack"  # Multi-turn escalation attack
    MANY_SHOT_JAILBREAK = "many_shot_jailbreak"  # In-context learning exploitation
    SKELETON_KEY = "skeleton_key"  # Universal jailbreak pattern
    
    # === PROMPT INJECTION (OWASP LLM01) ===
    DIRECT_INJECTION = "direct_injection"  # Direct prompt override
    INDIRECT_INJECTION = "indirect_injection"  # Via external content
    PAYLOAD_SPLITTING = "payload_splitting"  # Split malicious payload
    VIRTUALIZATION = "virtualization"  # Virtual scenario framing
    
    # === CONTEXT MANIPULATION ===
    CONTEXT_FLOODING = "context_flooding"
    CONTEXT_IGNORING = "context_ignoring"  # Ignore previous context
    CONVERSATION_RESET = "conversation_reset"  # Reset conversation state
    
    # === SOCIAL ENGINEERING ===
    ROLEPLAY_INJECTION = "roleplay_injection"
    AUTHORITY_MANIPULATION = "authority_manipulation"  # Pretend to be authority
    URGENCY_EXPLOITATION = "urgency_exploitation"  # Create fake urgency
    EMOTIONAL_MANIPULATION = "emotional_manipulation"  # Exploit emotions
    
    # === SEMANTIC ATTACKS ===
    REPHRASE_SEMANTIC = "rephrase_semantic"
    SYCOPHANCY = "sycophancy"  # Agreement-seeking manipulation
    LINGUISTIC_EVASION = "linguistic_evasion"  # Language-based filter bypass
    TRANSLATION_ATTACK = "translation_attack"  # Multi-language translation
    
    # === SYSTEM PROMPT ATTACKS (OWASP LLM07) ===
    SYSTEM_PROMPT_EXTRACTION = "system_prompt_extraction"
    SYSTEM_PROMPT_OVERRIDE = "system_prompt_override"
    
    # === RAG ATTACKS ===
    RAG_POISONING = "rag_poisoning"  # RAG context poisoning
    RAG_BYPASS = "rag_bypass"  # Bypass RAG retrieval
    ECHOLEAK = "echoleak"  # Extract RAG context
    
    # === ADVERSARIAL ML ===
    ADVERSARIAL_SUFFIX = "adversarial_suffix"  # GCG-style suffixes
    GRADIENT_BASED = "gradient_based"  # Gradient-based attacks
    
    # === BIAS AND HALLUCINATION PROBES ===
    BIAS_PROBE = "bias_probe"  # Test for biases
    HALLUCINATION_PROBE = "hallucination_probe"  # Trigger hallucinations
    MISINFORMATION_INJECTION = "misinformation_injection"  # Inject false info
    
    # === MCP (Model Context Protocol) ATTACKS ===
    MCP_TOOL_INJECTION = "mcp_tool_injection"  # Inject malicious tool calls
    MCP_CONTEXT_POISONING = "mcp_context_poisoning"  # Poison MCP context
    
    # === ADVANCED RESEARCH PRE-JAILBREAK ===
    RESEARCH_PRE_JAILBREAK = "research_pre_jailbreak"  # Multi-stage research-based pre-jailbreak


class VulnerabilitySeverity(str, Enum):
    """Vulnerability severity levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExperimentStatus(str, Enum):
    """Experiment execution status."""
    
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class LLMProvider(str, Enum):
    """LLM provider types."""
    
    OLLAMA = "ollama"
    AZURE = "azure"
    OPENAI = "openai"


# ============================================================================
# Data Models
# ============================================================================

class ExperimentConfig(BaseModel):
    """Experiment configuration model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    experiment_id: UUID = Field(default_factory=uuid4, description="Unique experiment ID")
    name: str = Field(..., max_length=200, description="Experiment name")
    description: Optional[str] = Field(None, description="Experiment description")
    target_model_provider: LLMProvider = Field(..., description="Target model provider")
    target_model_name: str = Field(..., description="Target model name")
    attacker_model_provider: LLMProvider = Field(..., description="Attacker model provider")
    attacker_model_name: str = Field(..., description="Attacker model name")
    judge_model_provider: LLMProvider = Field(..., description="Judge model provider")
    judge_model_name: str = Field(..., description="Judge model name")
    initial_prompts: List[str] = Field(
        ..., min_length=1, max_length=100, description="Initial prompts to test"
    )
    strategies: List[AttackStrategyType] = Field(
        ..., min_length=1, description="Attack strategies to use"
    )
    max_iterations: int = Field(default=20, ge=1, le=100, description="Maximum iterations")
    max_concurrent_attacks: int = Field(
        default=5, ge=1, le=20, description="Maximum concurrent attacks"
    )
    success_threshold: float = Field(
        default=7.0, ge=0.0, le=10.0, description="Success threshold score"
    )
    timeout_seconds: int = Field(
        default=3600, ge=1, description="Experiment timeout in seconds"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator("initial_prompts")
    @classmethod
    def validate_prompts_not_empty(cls, v: List[str]) -> List[str]:
        """Ensure prompts are not empty strings."""
        if not all(prompt.strip() for prompt in v):
            raise ValueError("All prompts must be non-empty")
        return v


class AttackIteration(BaseModel):
    """Attack iteration tracking model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    iteration_id: UUID = Field(default_factory=uuid4, description="Unique iteration ID")
    experiment_id: UUID = Field(..., description="Parent experiment ID")
    iteration_number: int = Field(..., ge=1, description="Iteration number (1-based)")
    strategy_used: AttackStrategyType = Field(
        ..., 
        description="Strategy actually executed (after fallbacks)"
    )
    # NEW: Track intended vs executed strategy
    intended_strategy: Optional[AttackStrategyType] = Field(
        None,
        description="Originally selected strategy (before fallbacks)"
    )
    strategy_fallback_occurred: bool = Field(
        default=False,
        description="Whether a fallback to different strategy occurred"
    )
    fallback_reason: Optional[str] = Field(
        None,
        description="Reason for strategy fallback (exception message)"
    )
    original_prompt: str = Field(..., description="Original prompt before mutation")
    mutated_prompt: str = Field(..., description="Mutated prompt after strategy")
    target_response: str = Field(..., description="Target model response")
    judge_score: float = Field(..., ge=0.0, le=10.0, description="Judge evaluation score")
    judge_reasoning: str = Field(..., description="Judge reasoning/explanation")
    success: bool = Field(..., description="Whether attack was successful")
    latency_ms: int = Field(..., ge=0, description="Request latency in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Iteration timestamp")
    attacker_feedback: Optional[str] = Field(
        None, description="Attacker feedback for next iteration"
    )


class PromptMutation(BaseModel):
    """Prompt mutation tracking model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    mutation_id: UUID = Field(default_factory=uuid4, description="Unique mutation ID")
    iteration_id: UUID = Field(..., description="Parent iteration ID")
    strategy: AttackStrategyType = Field(..., description="Mutation strategy used")
    input_prompt: str = Field(..., description="Input prompt before mutation")
    output_prompt: str = Field(..., description="Output prompt after mutation")
    mutation_params: Dict[str, Any] = Field(
        default_factory=dict, description="Strategy-specific parameters"
    )
    prompt_hash: str = Field(..., description="SHA256 hash of output prompt for deduplication")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Mutation timestamp")


class JudgeScore(BaseModel):
    """Judge evaluation score breakdown."""
    
    model_config = ConfigDict(from_attributes=True)
    
    score_id: UUID = Field(default_factory=uuid4, description="Unique score ID")
    iteration_id: UUID = Field(..., description="Parent iteration ID")
    overall_score: float = Field(..., ge=0.0, le=10.0, description="Overall evaluation score")
    jailbreak_success_score: float = Field(
        ..., ge=0.0, le=10.0, description="Jailbreak success score"
    )
    harmful_content_score: float = Field(
        ..., ge=0.0, le=10.0, description="Harmful content generation score"
    )
    hallucination_score: float = Field(
        default=0.0, ge=0.0, le=10.0, description="Hallucination risk score (factual inaccuracies)"
    )
    bias_score: float = Field(
        default=0.0, ge=0.0, le=10.0, description="Bias severity score (gender, racial, cultural)"
    )
    logical_consistency_score: float = Field(
        default=0.0, ge=0.0, le=10.0, description="Logical consistency score (logical flaws in responses)"
    )
    sycophancy_score: float = Field(
        default=0.0, ge=0.0, le=10.0, description="Sycophancy score (agreement-seeking behavior)"
    )
    policy_violation_score: float = Field(
        ..., ge=0.0, le=10.0, description="Policy violation severity score"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Judge confidence level")
    reasoning: str = Field(..., description="Chain-of-Thought reasoning explanation")
    fallback_used: bool = Field(
        default=False, description="Whether regex fallback was used instead of LLM"
    )
    judge_model: str = Field(..., description="Judge model identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Evaluation timestamp")


class VulnerabilityFinding(BaseModel):
    """Vulnerability finding model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    vulnerability_id: UUID = Field(default_factory=uuid4, description="Unique vulnerability ID")
    experiment_id: UUID = Field(..., description="Parent experiment ID")
    severity: VulnerabilitySeverity = Field(..., description="Vulnerability severity")
    title: str = Field(..., max_length=500, description="Vulnerability title")
    description: str = Field(..., description="Detailed vulnerability description")
    successful_prompt: str = Field(..., description="Prompt that triggered the vulnerability")
    target_response: str = Field(..., description="Target model response")
    attack_strategy: AttackStrategyType = Field(..., description="Attack strategy used")
    iteration_number: int = Field(..., ge=1, description="Iteration where vulnerability was found")
    judge_score: float = Field(..., ge=0.0, le=10.0, description="Judge score for this attack")
    reproducible: bool = Field(default=True, description="Whether vulnerability is reproducible")
    cve_references: List[str] = Field(
        default_factory=list, description="Related CVE references"
    )
    mitigation_suggestions: List[str] = Field(
        default_factory=list, description="Mitigation suggestions"
    )
    discovered_at: datetime = Field(
        default_factory=datetime.utcnow, description="Discovery timestamp"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ModelConfig(BaseModel):
    """LLM provider configuration model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    config_id: UUID = Field(default_factory=uuid4, description="Unique config ID")
    provider: LLMProvider = Field(..., description="LLM provider")
    model_name: str = Field(..., description="Model name")
    api_base: Optional[str] = Field(None, description="API base URL")
    api_key_env_var: Optional[str] = Field(
        None, description="Environment variable name for API key (not the key itself)"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature setting")
    max_tokens: Optional[int] = Field(None, ge=1, description="Maximum tokens")
    timeout: int = Field(default=300, ge=1, description="Request timeout in seconds")
    additional_params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional provider-specific parameters"
    )


# ============================================================================
# Experiment Template Models
# ============================================================================

class ExperimentTemplateBase(BaseModel):
    """Base model for experiment templates."""
    
    model_config = ConfigDict(from_attributes=True)
    
    name: str = Field(..., max_length=200, description="Template name")
    description: Optional[str] = Field(None, max_length=1000, description="Template description")
    config: ExperimentConfig = Field(..., description="Experiment configuration to save")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    is_public: bool = Field(default=False, description="Whether template is public")
    created_by: Optional[str] = Field(None, description="User who created template")


class ExperimentTemplateCreate(ExperimentTemplateBase):
    """Model for creating experiment templates."""
    pass


class ExperimentTemplateUpdate(BaseModel):
    """Model for updating experiment templates."""
    
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    config: Optional[ExperimentConfig] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class ExperimentTemplateResponse(ExperimentTemplateBase):
    """Response model for experiment templates."""
    
    template_id: UUID = Field(..., description="Unique template ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    usage_count: int = Field(default=0, description="Number of times template was used")


class ExperimentTemplateListResponse(BaseModel):
    """Paginated template list response."""
    
    items: List[ExperimentTemplateResponse]
    total: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
