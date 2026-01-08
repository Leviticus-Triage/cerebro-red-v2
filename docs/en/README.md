# CEREBRO-RED v2 Documentation

[🇬🇧 English](README.md) | [🇩🇪 Deutsch](../de/README.md)

Welcome to the CEREBRO-RED v2 documentation. This documentation provides comprehensive guides for using, configuring, deploying, and understanding the platform.

## 📚 Documentation Index

### Getting Started
- **[User Guide](user-guide.md)** - Complete guide to using CEREBRO-RED v2
  - Installation and setup
  - Creating and managing experiments
  - Understanding results and telemetry
  - Troubleshooting common issues

### Configuration
- **[Configuration Guide](configuration.md)** - Environment variables and settings
  - LLM provider configuration (Ollama, Azure OpenAI, OpenAI)
  - Database and storage settings
  - API security and authentication
  - Rate limiting and circuit breakers

### Deployment
- **[Deployment Guide](deployment.md)** - Production and demo deployment
  - Local Docker deployment
  - Railway cloud deployment
  - Environment setup and health checks
  - Demo mode configuration

### Technical Documentation
- **[Architecture](architecture.md)** - Technical architecture and design
  - System components and interactions
  - PAIR algorithm implementation
  - Data flow and telemetry
  - Performance considerations

- **[Security](security.md)** - Security best practices
  - API key management
  - Rate limiting strategies
  - Demo mode security
  - Data protection

## 🚀 Quick Links

- **Main Repository**: [github.com/Leviticus-Triage/cerebro-red-v2](https://github.com/Leviticus-Triage/cerebro-red-v2)
- **Quick Start**: See [User Guide - Installation](user-guide.md#installation)
- **API Reference**: Available at `/docs` endpoint when backend is running
- **Live Demo**: [Railway Demo Instance](https://cerebro-red-v2.railway.app) (read-only)

## 📖 Documentation Structure

```
docs/
├── en/                    # English documentation (primary)
│   ├── README.md         # This file - documentation hub
│   ├── user-guide.md     # Complete user documentation
│   ├── configuration.md  # Environment variables and settings
│   ├── deployment.md     # Deployment guides
│   ├── architecture.md  # Technical architecture
│   └── security.md       # Security considerations
├── de/                    # German documentation (secondary)
│   ├── README.md         # German documentation hub
│   ├── benutzerhandbuch.md
│   ├── konfiguration.md
│   └── bereitstellung.md
└── metadata.yml          # Documentation tracking metadata
```

## 🔄 Language Switching

Each document includes language switcher links at the top:
- **English** documents link to corresponding German translations
- **German** documents link back to English versions
- Use the language switcher to navigate between languages

## 📝 Contributing to Documentation

Documentation improvements are welcome! Please:
1. Follow the existing structure and style
2. Keep both English and German versions in sync
3. Use relative paths for internal links
4. Update `docs/metadata.yml` when adding new documents

## 🔗 External Resources

- **Research Paper**: [PAIR Algorithm](https://arxiv.org/abs/2310.08419)
- **Upstream Project**: [hexstrike-ai](https://github.com/0x4m4/hexstrike-ai)
- **Portfolio**: [exodus-hensen.site](https://exodus-hensen.site)

---

**Last Updated**: 2026-01-08  
**Documentation Version**: 2.0.0
