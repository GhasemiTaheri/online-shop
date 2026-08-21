# Codex Workflow

## Source-of-truth order

Before changing code, Codex should read repository `AGENTS.md`, this documentation index, relevant requirements, the accepted decision register, bounded-context rules, affected aggregate/event/API contract, and accepted ADRs. If documents conflict, stop and surface the conflict; do not guess silently. If a failure scenario has no clear documented recovery and the choice could change business state or data, preserve the available evidence and ask the user before implementing a policy.

## Vertical-slice sequence

For each significant feature:

1. Identify requirement IDs and bounded context.
2. State affected invariants and contracts.
3. Add/update domain and application tests.
4. Implement domain behavior.
5. Implement command/query handler and ports.
6. Add infrastructure mapping/repository or message adapter.
7. Add the HTTP/event entry point last.
8. Run focused checks, then the relevant wider suite.
9. Update docs/ADR when behavior or architecture changes.

## Recommended implementation slices

1. Project bootstrap and tooling.
2. Ordering domain (`Money`, address, OrderItem, Order, invariants).
3. Catalog product and create-order application contract.
4. MongoDB Order repository and create/get/list API.
5. Inventory aggregate, reservation algorithm, and concurrency tests.
6. Event envelope, Outbox publisher, RabbitMQ, and Inbox idempotency.
7. Fake Payment workflow and compensation.
8. Order confirmation and Fulfillment.
9. Cancellation/refund/release paths.
10. Observability, operational endpoints, integration/e2e/load tests, and README polish.

## Prompt template

```text
Read AGENTS.md and the relevant docs. Implement [one bounded feature] for [requirement IDs].

Constraints:
- Stay inside [bounded context].
- Preserve [named invariants/contracts].
- Do not implement [out-of-scope layers/features].
- Add the specified tests and run relevant checks.
- Report assumptions, changed files, checks run, and remaining risks.
```

## Review checklist

- Does business behavior live in the domain rather than HTTP/persistence code?
- Are cross-context boundaries respected?
- Are state changes behavioral and valid?
- Are event/outbox/idempotency/concurrency guarantees preserved?
- Are money, timestamps, secrets, and errors handled safely?
- Do tests prove both success and failure paths?
- Did the change avoid speculative abstractions and unrelated scope?

## Recommended repository instruction file

Create a root `AGENTS.md` that repeats non-negotiable dependency/boundary rules, commands, and the vertical-slice workflow. Keep detailed product knowledge here in `docs`; link rather than duplicating every requirement into `AGENTS.md`.
