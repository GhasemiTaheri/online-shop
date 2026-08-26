# Development Guidelines

## Architectural rules

- Keep domain modules free of frameworks and persistence concerns.
- Put business rules in aggregates, value objects, policies, or domain services—not routers or repository adapters.
- Keep HTTP routers thin: validate, authorize, invoke one use case, map results/errors.
- Define ports inward; infrastructure implements them.
- Do not import another bounded context's domain or infrastructure internals.
- Use explicit mappers between domain objects, HTTP schemas, event contracts, and MongoDB documents.
- Introduce shared abstractions only after at least two contexts need the same stable concept.

## Python rules

- Target Python 3.13 as currently declared by the project unless compatibility requirements change.
- Use type annotations, async only for I/O boundaries, timezone-aware UTC timestamps, and `Decimal` for money.
- Prefer immutable value objects and explicit domain exceptions.
- Do not expose raw database IDs, driver exceptions, stack traces, or secrets.
- Use named standard-library loggers and structured `extra` fields only at
  presentation, application, and infrastructure boundaries. Logs are JSON on
  stdout and may include only the documented observability fields; never log
  request bodies, payment tokens, credentials, or secrets.
- Keep commands imperative, events past tense, and query DTOs separate from aggregates.

## Tooling target

Use `uv` for dependency/environment management, Ruff for lint/format, mypy for type checking, and pytest/pytest-asyncio for tests. Put configuration in `pyproject.toml` unless a tool requires another file.

Expected commands after tooling is configured:

```text
uv sync
uv run uvicorn online_shop.main:app --reload
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

The current repository is only a scaffold; package paths and dependencies must be established during bootstrap.

## Change discipline

Each feature should update requirements/contracts and tests together. New architectural patterns require an ADR. Bug fixes should include a focused regression test when practical.
