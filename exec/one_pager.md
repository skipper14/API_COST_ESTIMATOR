# AfyaPlus: Cost-Optimised AI Deployment

**Decision brief | October 2026 | Planning estimate, USD**

## Recommendation

Retain a managed model API for the pilot and route eligible low-risk work to
`gpt-4o-mini`. Keep high-risk or ambiguous clinical cases on the existing
human-review path. Do not commit to GPU self-hosting at this traffic level.

## Unit economics

| Scenario | Requests/month | Total/1,000 | Monthly total |
| --- | ---: | ---: | ---: |
| Baseline | 100,000 | $5.3790 | $537.90 |
| Sustained 10x | 1,000,000 | $0.9790 | $979.01 |

The API token portion is $0.17901 per 1,000 under the 450-input / 180-output
token shape and 2% retry allowance. The rest is explicit infrastructure and
allocated people/ops planning assumptions, not a cloud quote. Rates still need
confirmation against the current OpenRouter route price.

## Operating choices

- **Scale:** 10x monthly volume raises estimated total monthly spend by 1.82x
  under the assumed platform allocations. It does not prove 10x capacity or
  latency; validate throughput, quotas, and p95 SLOs before launch.
- **Cache:** public FAQ fixtures produced a 62.5% hit rate (5/8) and reduced
  estimated token spend by 62.5%. TTL is five minutes. Never generalize this
  to patient-specific triage; the cache only accepts allow-listed FAQ IDs.
- **Batch:** group noninteractive work behind a queue and completion deadline.
  The local worker grouped 7 mock jobs into 2 batches; no provider discount or
  production throughput is claimed.
- **Controls:** proposed $1,000 monthly alert budget, 80% and 100% actual-spend
  notices, and a 100% forecast notice. Apply cost-center, environment, and
  workload tags. Alerts do not automatically stop spend. Bound autoscaling by
  quotas and use capped retries/circuit breakers to contain provider failures.
- **Fallback:** no paid cloud, Redis, GPU, Kubernetes, or live load test is
  claimed. Local Docker Compose and written Azure/AWS budget examples are the
  submission path; use fixtures before any paid-key test.

## Trade-off

Managed API deployment minimizes fixed serving and model-operations burden but
leaves per-token prices, quotas, and availability with the provider. The
self-host break-even is approximately 15.25M requests/month under the
illustrative $1/hour GPU plus 40 hours/month of model operations; this is a
planning threshold, not a procurement result. Confirm rates, load behavior,
quality, and staff effort before scaling. Serverless cold starts, prompt
compression, and any model/prompt A/B must be evaluated against p95 latency and
safety quality. Quantization, pruning, and KV-cache tuning are self-hosted
levers and are not claimed as API savings.