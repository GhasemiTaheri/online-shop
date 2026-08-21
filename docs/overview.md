# Project Overview

## Purpose

Online Shop demonstrates backend architecture through an order-fulfillment workflow built with FastAPI, MongoDB, DDD, asynchronous messaging, and a modular monolith.

## Primary scenario

1. A customer submits an order with an idempotency key.
2. Catalog data is validated and name/price snapshots are stored on the order.
3. Inventory reserves stock without overselling.
4. A fake payment provider authorizes or rejects payment.
5. Successful orders are confirmed and a shipment is created.
6. A shipment can be marked shipped and delivered.

Failure paths include insufficient stock, failed payment, cancellation, duplicate messages, retryable publishing failures, and concurrent inventory reservations.

## Goals

- Demonstrate behavior-rich aggregates, value objects, invariants, and domain events.
- Enforce bounded-context and layer boundaries.
- Demonstrate Outbox, idempotent consumers, optimistic concurrency, and observability.
- Provide focused unit, integration, API, messaging, and concurrency tests.
- Remain achievable in approximately 10–14 focused development days.

## Non-goals for version 1

- Production identity and access management.
- Real payment, tax, carrier, or notification integrations.
- Frontend, product images, reviews, recommendations, discounts, or search engine.
- Kubernetes or multiple microservice deployments.
- Exactly-once message delivery or cross-context distributed transactions.

Version 1 accepts a trusted `customer_id` and uses a development-only admin key. It must not be described as production-ready authentication or authorization.

## Success criteria

- The happy path completes from order placement to shipment creation.
- Defined failure and duplicate-delivery paths are deterministic and tested.
- Domain tests run without FastAPI, MongoDB, RabbitMQ, or Redis.
- Documentation, local setup, health checks, and architecture decisions are reviewable by a recruiter or interviewer.
