# External Evidence Guidance

Local evidence is mandatory. External references are optional and must not be invented.

Use external examples only when they are directly relevant and well-known enough to state safely. Prefer standards and framework docs over forced company references.

## Safe Reference Patterns

- **API contracts:** Stripe-style idempotency and backwards-compatible API evolution are useful references for retry-safe writes and stable envelopes.
- **Reliability:** Google SRE concepts are useful for error budgets, observability, incident review, and reducing toil.
- **Security:** OWASP guidance is appropriate for input validation, auth, secrets, injection, and logging sensitive data.
- **Distributed systems:** AWS architecture guidance is useful for retries with backoff, queues, idempotency, and failure isolation.
- **Frontend state:** React docs are appropriate for render lifecycle, batching, effects, and derived state.
- **Data/query correctness:** Database docs or query engine docs are better than company examples for SQL semantics, partition pruning, null behavior, and aggregation.

## Rules

- Do not claim a company had a specific incident unless you are sure.
- Do not add five external bullets by default. One strong reference is better than five weak ones.
- If no external reference naturally fits, write: `External reference: none needed; local evidence is sufficient.`
- If browsing is required for a precise citation, browse or omit the citation.
