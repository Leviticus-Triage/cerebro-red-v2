# Research References and Attribution

This document acknowledges the research projects, tools, and methodologies that inspired and informed the development of CEREBRO-RED v2.

## Core Research

### PAIR Algorithm

**Paper**: [Prompt Automatic Iterative Refinement (PAIR)](https://arxiv.org/abs/2310.08419)

**Authors**: Chao et al.

**Implementation**: CEREBRO-RED v2 implements the PAIR algorithm for automated prompt refinement and LLM security assessment.

**License**: Research paper (public domain)

---

## Third-Party Research Tools

The following research tools and frameworks provided inspiration and reference implementations for attack strategies. **Note**: CEREBRO-RED v2 does not include their source code, but implements similar attack methodologies.

### PyRIT (Microsoft)

**Repository**: [Azure/PyRIT](https://github.com/Azure/PyRIT)

**License**: MIT License

**Attribution**: Microsoft AI Red Team

**Contribution**: Reference implementation for red teaming methodologies and attack strategies.

**Status**: Not included in CEREBRO-RED v2 codebase. Implemented similar methodologies independently.

---

### LLAMATOR (ITMO University)

**Repository**: [LLAMATOR-Core/llamator](https://github.com/LLAMATOR-Core/llamator)

**License**: CC BY-NC-SA 4.0

**Attribution**: ITMO University

**Contribution**: Research on LLM attack strategies and evaluation methodologies.

**Status**: Not included in CEREBRO-RED v2 codebase. Implemented similar attack strategies independently.

---

### Model-Inversion-Attack-ToolBox

**Repository**: [ffhibnese/Model-Inversion-Attack-ToolBox](https://github.com/ffhibnese/Model-Inversion-Attack-ToolBox)

**License**: MIT License

**Attribution**: Original authors

**Contribution**: Reference for model inversion attack techniques.

**Status**: Not included in CEREBRO-RED v2 codebase. Implemented similar techniques independently.

---

### L1B3RT4S (Elder Plinius)

**Repository**: [elder-plinius/L1B3RT4S](https://github.com/elder-plinius/L1B3RT4S)

**License**: MIT License

**Attribution**: Elder Plinius

**Contribution**: Reference implementation for advanced jailbreak techniques.

**Status**: Not included in CEREBRO-RED v2 codebase. Implemented similar techniques independently.

---

## Standards and Guidelines

### OWASP Top 10 for LLM Applications 2025

**Source**: [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

**Contribution**: Framework for categorizing and understanding LLM vulnerabilities.

**Status**: Used as reference for attack strategy categorization.

---

### NVIDIA garak

**Repository**: [NVIDIA/garak](https://github.com/NVIDIA/garak)

**License**: Apache 2.0

**Attribution**: NVIDIA

**Contribution**: Reference for vulnerability scanning methodologies.

**Status**: Not included in CEREBRO-RED v2 codebase. Used as reference for attack strategy design.

---

## Additional Research

### Crescendo Attack

**Description**: Multi-turn escalation attack technique

**Contribution**: Implemented as one of 44 attack strategies

---

### Many-Shot Jailbreaking

**Description**: Technique using multiple examples to bypass safety measures

**Contribution**: Implemented as attack strategy

---

### Skeleton Key Universal Jailbreak

**Description**: Universal jailbreak technique

**Contribution**: Implemented as attack strategy

---

## Implementation Notes

CEREBRO-RED v2 is an **independent implementation** that:

1. **Does NOT include** source code from the above projects
2. **Implements similar methodologies** based on published research and documentation
3. **Provides proper attribution** to original research and tools
4. **Respects all licenses** and intellectual property rights

All attack strategies in CEREBRO-RED v2 are implemented from scratch based on:
- Published research papers
- Public documentation
- Standard security testing methodologies
- Independent research and experimentation

## License Compatibility

CEREBRO-RED v2 is licensed under **Apache License 2.0**, which is compatible with:
- MIT License (PyRIT, Model-Inversion-Attack-ToolBox, L1B3RT4S)
- Apache 2.0 (garak)
- CC BY-NC-SA 4.0 (LLAMATOR - referenced only, not included)

## Citation

If you use CEREBRO-RED v2 in your research, please cite:

1. **CEREBRO-RED v2**: This repository
2. **PAIR Algorithm**: [Chao et al., 2023](https://arxiv.org/abs/2310.08419)
3. **Referenced Tools**: As appropriate for methodologies used

---

**Last Updated**: 2026-01-08  
**License**: Apache 2.0  
**Copyright**: 2024-2026 Leviticus-Triage
