# External Repository Integration

## Overview
CEREBRO-RED v2 integrates jailbreak techniques from multiple open-source projects. All integrations maintain proper attribution and comply with original licenses.

## Integrated Repositories

### 1. PyRIT (Microsoft)
- **Source**: https://github.com/Azure/PyRIT
- **License**: MIT License
- **Authors**: Microsoft AI Red Team
- **Integrated Techniques**:
  - DAN (Do Anything Now) variants (dan_1 through dan_11)
  - AIM (Always Intelligent and Machiavellian)
  - DUDE (Do Anything Now) variants (dude_1, dude_2, dude_3)
  - Developer Mode bypasses
  - Many-shot jailbreaking
  - Skeleton Key universal jailbreak
  - Crescendo Attack (multi-turn escalation)
  - Arth Singh advanced techniques (few-shot escalation, context flooding, etc.)
- **CEREBRO Strategies**: `jailbreak_dan`, `jailbreak_aim`, `jailbreak_dude`, `jailbreak_developer_mode`, `many_shot_jailbreak`, `crescendo_attack`, `skeleton_key`, `research_pre_jailbreak`
- **Templates Added**: 90+ YAML templates converted to JSON

### 2. L1B3RT4S
- **Source**: https://github.com/elder-plinius/L1B3RT4S
- **License**: MIT License
- **Authors**: Elder Plinius
- **Integrated Techniques**:
  - Emoji-based encoding (hyper-token-efficient attacks)
  - Leetspeak with custom dividers
  - GODMODE custom instructions
  - Steganographic text hiding
  - Multi-provider jailbreaks (OpenAI, Anthropic, Google, etc.)
  - Morse code obfuscation
  - Binary encoding
- **CEREBRO Strategies**: `obfuscation_unicode`, `obfuscation_leetspeak`, `obfuscation_token_smuggling`, `obfuscation_morse`, `obfuscation_binary`
- **Templates Added**: 40+ markdown-extracted prompts

### 3. LLAMATOR
- **Source**: https://github.com/LLAMATOR-Core/llamator
- **License**: CC BY-NC-SA 4.0
- **Authors**: Roman Neronov, Timur Nizamov, Nikita Ivanov
- **Integrated Techniques**:
  - RAG-specific attacks (context poisoning, bypass)
  - VLM (Vision-Language Model) attacks
  - OWASP LLM Top 10 aligned techniques
  - Direct and indirect prompt injection
- **CEREBRO Strategies**: `rag_poisoning`, `rag_bypass`, `virtualization`, `direct_injection`, `indirect_injection`
- **Templates Added**: 15+ RAG/VLM-specific templates

### 4. Model-Inversion-Attack-ToolBox
- **Source**: https://github.com/ffhibnese/Model-Inversion-Attack-ToolBox
- **License**: MIT License
- **Authors**: Yixiang Qiu, Hongyao Yu, Hao Fang, et al.
- **Integrated Techniques**:
  - System prompt extraction techniques
  - Gradient-based adversarial attacks (GCG-style)
- **CEREBRO Strategies**: `system_prompt_extraction`, `gradient_based`
- **Templates Added**: 10+ model inversion techniques

## Attribution in Code
All integrated techniques include attribution metadata:
```python
params = {
    "template_type": "jailbreak_dan",
    "source": "PyRIT dan_1.yaml",
    "authors": ["Alex Albert"],
    "license": "MIT",
    ...
}
```

## License Compliance
- **PyRIT (MIT)**: ✅ Commercial use allowed, attribution provided
- **L1B3RT4S (MIT)**: ✅ Commercial use allowed, attribution provided
- **LLAMATOR (CC BY-NC-SA 4.0)**: ⚠️ Non-commercial only, attribution provided
- **Model-Inversion-Attack-ToolBox (MIT)**: ✅ Commercial use allowed, attribution provided

**Note**: CEREBRO-RED v2 is a research tool. Ensure compliance with all upstream licenses before commercial use.

## Implementation Details

### Extraction Scripts
- `backend/scripts/extract_pyrit_templates.py`: Parses PyRIT YAML files and converts to JSON
- `backend/scripts/extract_l1b3rt4s_prompts.py`: Extracts L1B3RT4S markdown prompts

### Payload Storage
- `backend/data/advanced_payloads.json`: Central repository for all attack templates
- Version: 2.1.0
- Total categories: 36+
- Total templates: 150+

### Mutator Integration
All integrated strategies are implemented in `backend/core/mutator.py` with:
- PayloadManager integration for template loading
- Fallback mechanisms for robustness
- Comprehensive error logging
- Attribution metadata in all responses

## References
- PyRIT: https://github.com/Azure/PyRIT
- L1B3RT4S: https://github.com/elder-plinius/L1B3RT4S
- LLAMATOR: https://github.com/LLAMATOR-Core/llamator
- Model-Inversion-Attack-ToolBox: https://github.com/ffhibnese/Model-Inversion-Attack-ToolBox
- OWASP LLM Top 10: https://genai.owasp.org/

## Citation
If you use CEREBRO-RED v2 in your research, please cite the original sources:

```bibtex
@software{pyrit2024,
  title={PyRIT: Python Risk Identification Toolkit for Generative AI},
  author={Microsoft AI Red Team},
  year={2024},
  url={https://github.com/Azure/PyRIT}
}

@software{l1b3rt4s2024,
  title={L1B3RT4S: Advanced LLM Jailbreak Techniques},
  author={Elder Plinius},
  year={2024},
  url={https://github.com/elder-plinius/L1B3RT4S}
}

@software{llamator2024,
  title={LLAMATOR: LLM Vulnerability Scanner},
  author={Neronov, Roman and Nizamov, Timur and Ivanov, Nikita},
  year={2024},
  url={https://github.com/LLAMATOR-Core/llamator}
}
```
