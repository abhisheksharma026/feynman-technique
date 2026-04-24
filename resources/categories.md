# Feynman Technique Categories

Assign exactly one primary category. Add impact and surface metadata separately.

## Primary Categories

| Category | Use when |
|---|---|
| `mental-model` | The key issue was misunderstanding how a system, API, framework, or runtime works. |
| `contract` | An interface, schema, API response, data model, or component contract was assumed incorrectly. |
| `state` | State was stale, mutated unexpectedly, cached too long, or not synchronized. |
| `timing` | Race condition, ordering dependency, async lifecycle, retry, debounce, or scheduling issue. |
| `data` | Wrong column, bad query, denominator error, schema mismatch, encoding, or malformed data shape. |
| `config` | Environment, feature flag, build, dependency, routing, or deployment config. |
| `edge-case` | Null, empty, boundary, low-volume, overflow, permission, or rare branch. |
| `design` | The abstraction, architecture, ownership, or component boundary was wrong. |
| `testing` | The issue escaped because tests were missing, shallow, over-mocked, or asserted the wrong contract. |
| `operations` | Monitoring, logging, retry, job, cache, migration, or production-readiness gap. |

## Impact

- `low`: local inconvenience or docs/test-only issue
- `medium`: feature bug with contained blast radius
- `high`: user-facing workflow, data correctness, or reliability issue
- `critical`: security, data loss, billing, auth, outage, or broad production breakage

## Surface

Use one: `frontend`, `backend`, `data`, `infra`, `agent`, `analytics`, `test`, `docs`, `product`, `security`.

## Detection

Optional metadata if useful: `manual`, `test`, `review`, `logs`, `prod`, `user-report`, `static-analysis`.
