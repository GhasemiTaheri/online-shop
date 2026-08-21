# Online Shop Documentation

This directory is the source of truth for the Online Shop portfolio project: a FastAPI, MongoDB, domain-driven, event-driven order-fulfillment backend.

## Reading order

1. [Project overview](overview.md)
2. [Functional requirements](requirements/functional-requirements.md)
3. [Non-functional requirements](requirements/non-functional-requirements.md)
4. [Architecture overview](architecture/overview.md)
5. [Bounded contexts](architecture/bounded-contexts.md)
6. [Domain model](domain/domain-model.md)
7. [API contract](api/endpoints.md)
8. [Event catalog](events/event-catalog.md)
9. [MongoDB design](database/mongodb-design.md)
10. [Development guidelines](development/coding-guidelines.md)
11. [Testing strategy](development/testing-strategy.md)
12. [Codex workflow](development/codex-workflow.md)
13. [Decision register](requirements/open-questions.md)

## Decision status

Architectural decisions are recorded as ADRs under [`adr/`](adr/). Accepted scope and domain decisions are centralized in the [decision register](requirements/open-questions.md). Requirements use stable IDs so code, tests, pull requests, and ADRs can refer to them.

## Scope guardrail

Version 1 is a polished modular monolith, not a production marketplace. It deliberately excludes a frontend, real card handling, Kubernetes, advanced catalog features, and multiple deployed microservices.
