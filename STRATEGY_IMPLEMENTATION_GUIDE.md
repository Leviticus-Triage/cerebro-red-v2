# CEREBRO-RED v2: Attack Strategy Implementation Guide

## Overview
All 44 attack strategies are now fully implemented across three layers:
1. **Enum Definition** (`backend/core/models.py`) - Type definitions
2. **Mutator Methods** (`backend/core/mutator.py`) - Main mutation logic
3. **Strategy Registry** (`backend/core/attack_strategies.py`) - Reusable strategy classes

## Strategy Mapping Table

| # | Strategy | Mutator Method | Registry Class | Payload Category | Source |
|---|----------|----------------|----------------|------------------|--------|
| 1 | obfuscation_base64 | `_mutate_base64()` | Base64ObfuscationStrategy | obfuscation_base64 | Existing |
| 2 | obfuscation_leetspeak | `_mutate_leetspeak()` | LeetSpeakObfuscationStrategy | obfuscation_leetspeak | Existing |
| 3 | obfuscation_rot13 | `_mutate_rot13()` | ROT13ObfuscationStrategy | obfuscation_rot13 | Existing |
| 4 | obfuscation_ascii_art | `_mutate_obfuscation_ascii_art()` | ASCIIArtObfuscationStrategy | obfuscation_ascii_art_templates | Phase 2 |
| 5 | obfuscation_unicode | `_mutate_obfuscation_unicode()` | UnicodeObfuscationStrategy | obfuscation_unicode_templates | Phase 2 |
| 6 | obfuscation_token_smuggling | `_mutate_obfuscation_token_smuggling()` | TokenSmugglingStrategy | obfuscation_token_smuggling_templates | Phase 2 |
| 7 | obfuscation_morse | `_mutate_obfuscation_morse()` | MorseObfuscationStrategy | obfuscation_morse_templates | Phase 2 |
| 8 | obfuscation_binary | `_mutate_obfuscation_binary()` | BinaryObfuscationStrategy | obfuscation_binary_templates | Phase 2 |
| 9 | jailbreak_dan | `_mutate_jailbreak_dan()` | DANJailbreakStrategy | jailbreak_dan_templates | PyRIT |
| 10 | jailbreak_aim | `_mutate_jailbreak_aim()` | AIMJailbreakStrategy | jailbreak_aim_templates | PyRIT |
| 11 | jailbreak_stan | `_mutate_jailbreak_stan()` | STANJailbreakStrategy | jailbreak_stan_templates | Phase 2 |
| 12 | jailbreak_dude | `_mutate_jailbreak_dude()` | DUDEJailbreakStrategy | jailbreak_dude_templates | Phase 2 |
| 13 | jailbreak_developer_mode | `_mutate_jailbreak_developer_mode()` | DeveloperModeJailbreakStrategy | jailbreak_developer_mode_templates | Phase 2 |
| 14 | crescendo_attack | `_mutate_crescendo_attack()` | CrescendoAttackStrategy | crescendo_attack_templates | Phase 2 |
| 15 | many_shot_jailbreak | `_mutate_many_shot_jailbreak()` | ManyShotJailbreakStrategy | many_shot_jailbreak_templates | Phase 2 |
| 16 | skeleton_key | `_mutate_skeleton_key()` | SkeletonKeyStrategy | jailbreak_skeleton_key_templates | Phase 2 |
| 17 | direct_injection | `_mutate_direct_injection()` | DirectInjectionStrategy | llm01_prompt_injection | Existing |
| 18 | indirect_injection | `_mutate_indirect_injection()` | IndirectInjectionStrategy | indirect_injection_templates | Phase 2 |
| 19 | payload_splitting | `_mutate_payload_splitting()` | PayloadSplittingStrategy | - | Phase 2 |
| 20 | virtualization | `_mutate_virtualization()` | VirtualizationStrategy | hypothetical_framing | Phase 2 |
| 21 | context_flooding | `_mutate_context_flooding()` | - | context_flooding | Existing |
| 22 | context_ignoring | `_mutate_context_ignoring()` | ContextIgnoringStrategy | context_ignoring_templates | Phase 2 |
| 23 | conversation_reset | `_mutate_conversation_reset()` | ConversationResetStrategy | conversation_reset_templates | Phase 2 |
| 24 | roleplay_injection | `_mutate_roleplay_injection()` | - | jailbreak_techniques | Existing |
| 25 | authority_manipulation | `_mutate_authority_manipulation()` | AuthorityManipulationStrategy | authority_manipulation_templates | Phase 2 |
| 26 | urgency_exploitation | `_mutate_urgency_exploitation()` | UrgencyExploitationStrategy | urgency_exploitation_templates | Phase 2 |
| 27 | emotional_manipulation | `_mutate_emotional_manipulation()` | EmotionalManipulationStrategy | emotional_manipulation_templates | Phase 2 |
| 28 | rephrase_semantic | `_mutate_rephrase_semantic()` | - | - | Existing (PAIR) |
| 29 | sycophancy | `_mutate_sycophancy()` | - | sycophancy_attacks | Existing |
| 30 | linguistic_evasion | `_mutate_linguistic_evasion()` | - | linguistic_evasion | Existing |
| 31 | translation_attack | `_mutate_translation_attack()` | TranslationAttackStrategy | translation_attack_templates | Phase 2 |
| 32 | system_prompt_extraction | `_mutate_system_prompt_extraction()` | SystemPromptExtractionStrategy | llm07_system_prompt_leakage | Existing |
| 33 | system_prompt_override | `_mutate_system_prompt_override()` | SystemPromptOverrideStrategy | system_prompt_override_templates | Phase 2 |
| 34 | rag_poisoning | `_mutate_rag_poisoning()` | RAGPoisoningStrategy | rag_poisoning_templates | Phase 2 |
| 35 | rag_bypass | `_mutate_rag_bypass()` | RAGBypassStrategy | rag_specific_attacks | Phase 2 |
| 36 | echoleak | `_mutate_echoleak()` | EchoLeakStrategy | echoleak_rag_attacks | Phase 2 |
| 37 | adversarial_suffix | `_mutate_adversarial_suffix()` | AdversarialSuffixStrategy | adversarial_suffix_templates | Phase 2 |
| 38 | gradient_based | `_mutate_gradient_based()` | GradientBasedStrategy | gradient_based_templates | Phase 2 |
| 39 | bias_probe | `_mutate_bias_probe()` | BiasProbeStrategy | - | Phase 2 |
| 40 | hallucination_probe | `_mutate_hallucination_probe()` | HallucinationProbeStrategy | - | Phase 2 |
| 41 | misinformation_injection | `_mutate_misinformation_injection()` | MisinformationInjectionStrategy | misinformation_injection_templates | Phase 2 |
| 42 | mcp_tool_injection | `_mutate_mcp_tool_injection()` | MCPToolInjectionStrategy | - | Phase 2 |
| 43 | mcp_context_poisoning | `_mutate_mcp_context_poisoning()` | MCPContextPoisoningStrategy | mcp_context_poisoning_templates | Phase 2 |
| 44 | research_pre_jailbreak | `_mutate_research_pre_jailbreak()` | ResearchPreJailbreakStrategy | research_pre_jailbreak_templates | Phase 2 |

## Implementation Patterns

### Pattern 1: PayloadManager-First
```python
def _mutate_{strategy}(self, prompt: str) -> Tuple[str, Dict[str, Any]]:
    try:
        templates = self.payload_manager.get_templates("{strategy}_templates")
        template = random.choice(templates)
        mutated = template.replace("{original_prompt}", prompt)
        return mutated, {"template_source": "payloads.json"}
    except (KeyError, ValueError) as e:
        # Hardcoded fallback
        mutated = f"[Fallback] {prompt}"
        return mutated, {"template_source": "hardcoded", "fallback": True}
```

### Pattern 2: Registry-First
```python
def _mutate_{strategy}(self, prompt: str) -> Tuple[str, Dict[str, Any]]:
    return self._mutate_via_registry(prompt, AttackStrategyType.{STRATEGY})
```

### Pattern 3: Hybrid (Registry + PayloadManager)
```python
def _mutate_{strategy}(self, prompt: str) -> Tuple[str, Dict[str, Any]]:
    try:
        # Try registry first
        return self._mutate_via_registry(prompt, AttackStrategyType.{STRATEGY})
    except Exception:
        # Fallback to PayloadManager
        templates = self.payload_manager.get_templates("{strategy}_templates")
        ...
```

## Testing
Run: `pytest tests/test_mutator_all_strategies.py -v`
Expected: 44/44 strategies pass

## Phase 2 Implementation Status

✅ **Schritt 1**: PyRIT Template-Extraktion Script erstellt (`scripts/extract_pyrit_templates.py`)
✅ **Schritt 2**: Payload-Kategorien erweitert (24 neue Kategorien in `payloads.json`)
✅ **Schritt 3**: Mutator-Methoden implementiert (36 neue `_mutate_*()` Methoden)
✅ **Schritt 4**: Strategy-Dispatch-Integration (vollständige Dispatch-Map für alle 44 Strategien)
✅ **Schritt 5**: Attack Strategies Registry Integration (alle Strategien registriert)
✅ **Schritt 6**: Mutator-Registry-Bridge Helper (`_mutate_via_registry()`)
✅ **Schritt 7**: Comprehensive Testing (`test_mutator_all_strategies.py` aktualisiert)
✅ **Schritt 8**: Dokumentation (dieses Dokument)

## Validation

- ✅ All 44 strategies have `_mutate_*()` methods in `mutator.py`
- ✅ All strategies are registered in `attack_strategies.py` registry
- ✅ All strategies have payload templates in `payloads.json`
- ✅ All strategies return proper metadata with `template_source`
- ✅ Fallback mechanisms in place (Registry → PayloadManager → Hardcoded)
