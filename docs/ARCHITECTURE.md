# Architecture Documentation

This document provides a comprehensive overview of the Cerebro-Red v2 architecture, including system design, component interactions, and data flow diagrams.

**Last Updated:** 2026-01-17  
**Version:** 2.0.0

---

## System Overview

Cerebro-Red v2 is a containerized platform for automated LLM security testing. The architecture follows a client-server model with real-time communication capabilities.

![Architecture Overview](images/architecture-overview-2026-01-06.jpeg)

*Figure 1: High-level system architecture showing the main components and their interactions.*

---

## Component Architecture

### Backend (FastAPI)

The backend is built on FastAPI with async/await support for high-performance concurrent operations.

![Backend Architecture](images/architecture-system-2026-01-03.jpeg)

*Figure 2: Backend system architecture with core modules and their relationships.*

**Key Components:**
- **Orchestrator**: Async batch processing with exponential backoff
- **Mutator**: PAIR algorithm with mutation strategies
- **Judge**: LLM-as-a-Judge with Chain-of-Thought evaluation
- **Telemetry**: Thread-safe JSONL audit logger

### Frontend (React)

The frontend provides a modern, responsive dashboard for experiment management and real-time monitoring.

![Frontend Dashboard](images/frontend-dashboard-2025-12-23.jpeg)

*Figure 3: Frontend dashboard showing experiment management interface.*

![Frontend Experiments](images/frontend-experiments-2025-12-23.jpeg)

*Figure 4: Experiment management view with real-time status updates.*

---

## Data Flow

The following diagram illustrates the data flow through the system:

![Data Flow Diagram](images/architecture-flow-2026-01-06.jpeg)

*Figure 5: Data flow from user interaction through API to LLM providers and back.*

### Request Flow

1. **User Request**: Frontend sends HTTP/WebSocket request to backend
2. **API Layer**: FastAPI routes request to appropriate handler
3. **Orchestrator**: Manages experiment lifecycle and task queue
4. **Mutator**: Generates adversarial prompts using PAIR algorithm
5. **LLM Provider**: Sends prompts to configured LLM (Ollama/OpenAI/Azure)
6. **Judge**: Evaluates LLM responses for vulnerabilities
7. **Telemetry**: Logs all operations to audit log
8. **Response**: Results sent back to frontend via WebSocket

---

## Core Modules

### Orchestrator

The orchestrator manages the experiment lifecycle and coordinates between components.

![Orchestrator Components](images/architecture-components-2026-01-03.jpeg)

*Figure 6: Orchestrator component architecture showing task management and coordination.*

### Integration Points

The system integrates with multiple LLM providers and external services:

![Integration Diagram](images/detail-integration-2026-01-03.jpeg)

*Figure 7: Integration points with LLM providers and external services.*

---

## Database Schema

The system uses SQLite for experiment data and JSONL for audit logs.

![Database Schema](images/detail-architecture-2026-01-03.jpeg)

*Figure 8: Database schema showing relationships between entities.*

---

## API Architecture

The REST API follows RESTful principles with WebSocket support for real-time updates.

![API Architecture](images/detail-api-2026-01-03.jpeg)

*Figure 9: API endpoint structure and request/response flow.*

---

## Deployment Architecture

The system is designed for containerized deployment with Docker.

![Deployment Diagram](images/detail-deployment-2025-12-24.jpeg)

*Figure 10: Deployment architecture showing container structure and networking.*

---

## Monitoring & Telemetry

The system includes comprehensive monitoring and telemetry capabilities.

![Monitoring Dashboard](images/frontend-monitoring-2025-12-23.jpeg)

*Figure 11: Real-time monitoring dashboard with metrics and status indicators.*

![Telemetry View](images/frontend-telemetry-2026-01-03.jpeg)

*Figure 12: Telemetry view showing detailed audit logs and system events.*

---

## Configuration Management

Configuration is managed through environment variables and configuration files.

![Configuration Diagram](images/detail-config-2025-12-23.jpeg)

*Figure 13: Configuration management showing environment variables and their usage.*

---

## Security Architecture

The system implements multiple security layers:

- **API Key Authentication**: Optional API key protection
- **Rate Limiting**: Prevents abuse and DoS attacks
- **CORS Configuration**: Secure cross-origin resource sharing
- **Circuit Breakers**: Prevents cascading failures
- **Audit Logging**: Comprehensive security event logging

![Security Components](images/detail-components-2026-01-03.jpeg)

*Figure 14: Security components and their interactions.*

---

## Performance Considerations

The architecture is optimized for performance and scalability:

- **Async/Await**: Non-blocking I/O operations
- **Connection Pooling**: Efficient database connection management
- **Caching**: Strategic caching of frequently accessed data
- **Circuit Breakers**: Automatic failure recovery
- **Rate Limiting**: Resource protection and fair usage

![Performance Metrics](images/detail-performance-2026-01-08.jpeg)

*Figure 15: Performance monitoring showing system metrics and resource usage.*

---

## Development Workflow

The development workflow includes testing, deployment, and monitoring phases.

![Development Workflow](images/detail-workflow-2026-01-03.jpeg)

*Figure 16: Development workflow from code to deployment.*

---

## Additional Resources

- [API Reference](en/api-reference.md) - Complete API endpoint documentation
- [Deployment Guide](DEPLOYMENT.md) - Deployment instructions and best practices
- [User Guide](en/user-guide.md) - User documentation and tutorials

---

**Note**: All diagrams and screenshots in this document are from actual system deployments and reflect the current architecture as of January 2026.
