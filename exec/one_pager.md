# AfyaPlus | Cost-Optimised AI Deployment

**Executive decision brief | October 2026 | USD planning estimates**

## Decision: Conditional Go

**GO** for a small, human-reviewed pilot on the managed API path. **NO-GO** for
autonomous clinical decisions or a production 10x launch until the budget,
service-level target, current provider rates, and safety checks below pass.
The locally runnable API is a deterministic clinic-catalog fallback; it does
not call a live model provider.

## Cost and spike plan

| Workload | Monthly requests | Total / 1,000 | Monthly estimate |
| --- | ---: | ---: | ---: |
| Baseline | 100,000 | $5.3790 | $537.90 |
| Sustained 10x scenario | 1,000,000 | $0.9790 | $979.01 |

At 10x, estimated monthly spend is $979.01 against the proposed $1,000 alert
budget, leaving only $20.99 of modeled headroom. This is not a guarantee of
capacity: use a staged traffic ramp, maximum concurrency, provider quotas, and
a queue for non-urgent work. Pause the ramp if projected spend exceeds budget,
error/retry rates rise, or the latency target is missed.

The model assumes 450 input tokens, 180 output tokens, a 2% retry allowance,
and inherited `gpt-4o-mini` rates that must be verified. Infrastructure and
people/operations costs are scenario allocations, not cloud quotes.

## Two measured levers

- **Public FAQ cache:** on 8 sample questions, 5 were served from cache (62.5%);
  estimated token cost fell from $0.17901 to $0.06713 per 1,000 requests. Cached
  answers expire after five minutes.
  All 8 cached answers matched their fixture source; that is not a medical
  quality or safety evaluation. Do not cache patient-specific answers.
- **Offline batch queue:** grouped 7 local jobs into 2 groups, 71.4% fewer
  work groups. This is a local processing measurement only; no bulk-pricing discount,
  production throughput, or latency gain is claimed.

## Risk, controls, and conditions

**Main risk:** demand or retries push spend past the cap while slowing responses.
Mitigate with $1,000/month budget notices at 80% actual ($800), 100% actual
($1,000), and 100% forecast; tag cost center, environment, and workload; cap
concurrency/retries; use a circuit breaker; and route uncertainty to human
review. These alerts notify operators; they do not stop spend automatically.

The interactive target is p95 below 2 seconds. **p95** means 95 out of 100
requests finish within that time. Before expanding traffic, verify the current
API rate, demonstrate that p95 and safety quality hold under a controlled load
test, and keep fallback behavior available. No paid cloud, Redis, GPU, or live
10x test was used; local Docker Compose, in-memory fixtures, and config-only
Azure/AWS budgets are the declared fallbacks.

**Recommendation:** pilot with these controls; do not approve autonomous
clinical use or claim 10x readiness until the conditions above are evidenced.
Full assumptions: [`cost/cost_model.md`](../cost/cost_model.md) and
[`memo/api_vs_selfhost.md`](../memo/api_vs_selfhost.md).