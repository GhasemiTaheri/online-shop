# Logging

The API and future worker processes use Python standard-library logging with one
JSON record per line written to stdout. Configure the minimum level with
`APP_LOG_LEVEL`; accepted values are `DEBUG`, `INFO` (the default), `WARNING`,
`ERROR`, and `CRITICAL`.

Every record contains UTC `timestamp`, `level`, `logger`, `message`, and the
current `correlation_id` and `causation_id` when available. The only permitted
additional fields are `context`, `operation`, `aggregate_type`, `aggregate_id`,
`event_id`, `event_type`, `attempt`, `duration_ms`, `status_code`, and
`error_code`.

HTTP middleware creates or accepts `X-Correlation-ID`, binds it for the lifetime
of the request, and echoes it back to clients. Integration-event publishers must
write the active correlation ID into their event envelope; consumers must bind
the envelope correlation and causation IDs before handling the event.

Expected custom exceptions log their stable error code without a traceback.
Unexpected errors log a traceback at `ERROR`. Never include request bodies,
payment tokens, credentials, secrets, or raw database/broker error payloads in
logs.
