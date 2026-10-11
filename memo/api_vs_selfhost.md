# Architecture Trade-off Memo: Managed API vs Self-Hosted OSS

**Decision:** use a managed API for the pilot; do not buy or reserve GPU capacity
yet. Revisit self-hosting only after measured traffic, quality, and GPU capacity
cross the gates below.

This is a planning comparison for a future text-generation workload routed to
`gpt-4o-mini`, not a bill from the running service. The runnable Week 6 API's
`/agent/ask` path is a deterministic MCP-backed clinic lookup and made no model
calls during local validation. No open-source model, GPU, quantized model, or
self-hosted serving stack was run for this comparison.

## Workload Comparison

| Dimension | Managed API | Self-hosted open-source model |
| --- | --- | --- |
| Cost shape | Pay per input/output token; low commitment and variable spend | Fixed GPU/runtime plus engineering and on-call; economical only with sufficient sustained utilization |
| Modeled cost | $0.17901 per 1,000 requests for the token shape and retry assumption below | Illustrative floor of $2,730/month before redundant capacity, storage, network, monitoring, and serving engineering |
| Scale and latency | Provider handles model capacity, subject to quota, routing, network latency, and rate limits | Team owns queueing, GPU sizing, autoscaling, cold/warm behavior, deployment, and capacity headroom |
| Operations | Provider manages model serving; team still owns API, retries, circuit breaker, secrets, and observability | Team patches runtime/model, manages weights and GPUs, responds to incidents, and validates upgrades |
| Quality and control | Fast model swaps, but provider behavior and price can change; prompts and outputs still need evaluation | More control over weights, quantization, and data path; every model/runtime change needs safety, quality, and latency evaluation |
| Best fit | Pilot, uncertain or bursty traffic, and workloads below measured break-even | Stable high volume with proven GPU utilization, staffing, and quality parity, or a hard data/residency requirement |

For this workload, the managed path is lower-risk at 100k and 1M requests/month.
The cost model estimates full API TCO of **$537.90/month at 100k** and
**$979.01/month at 1M** after its separate infrastructure and people/ops
allocations. At 1M, the API token component alone is **$179.01/month**. Do not
compare the full API TCO to the self-host floor as if the categories were equal:
the self-host figure below is only the incremental model-serving floor.

## Break-Even Sketch

| Input | Explicit assumption |
| --- | ---: |
| Average request | 450 input + 180 output tokens |
| Exercise token rates | $0.15 / 1M input; $0.60 / 1M output |
| Billed retry allowance | 2% additional attempts with same token shape |
| API variable cost | $0.00017901/request, or $0.17901/1,000 |
| GPU rental sensitivity | $1/hour x 730 hours = $730/month; not a quote |
| Model operations sensitivity | 40 hours/month x $50/hour = $2,000/month; not measured staffing |
| Self-host serving floor | $2,730/month before omitted costs |

```text
API cost/request = ((450 x $0.15) + (180 x $0.60)) / 1,000,000 x 1.02
                 = $0.00017901
Raw crossover    = $2,730 / $0.00017901
                 = about 15.25 million requests/month
```

| Monthly requests | API token spend | Self-host floor | Cost-only read |
| ---: | ---: | ---: | --- |
| 100,000 | $17.90 | $2,730 | API clearly lower |
| 1,000,000 | $179.01 | $2,730 | API clearly lower |
| 15,250,000 | about $2,729.90 | $2,730 | Raw crossover only; self-host omitted costs move it higher |

The rates are inherited exercise inputs, not independently confirmed current
OpenRouter rates; see the [cost model](../cost/cost_model.md) for provenance.
The $1/hour GPU and labor assumptions are sensitivities, not
vendor pricing, measured utilization, or a claim that one GPU can serve this
volume at the required latency. The calculation excludes GPU replicas or
headroom, storage, egress, monitoring, security, deployment engineering, idle
capacity, incident response, and any differences in API hosting shared by both
designs. Thus **15.25M is a screening threshold, not a decision-ready purchase
order**; the actual self-host crossover may be much higher or infeasible at
that traffic without additional GPUs.

## What Would Change the Decision

Move to a self-host evaluation only if at least one condition is demonstrated:

- Verified provider rates and sustained eligible traffic put API token spend
  above a fully loaded GPU/runtime and staffing quote, with capacity margin.
- A representative load test proves GPU tokens/second, peak concurrency,
  p95 latency, availability, and cost at the target request rate.
- A held-out quality/safety evaluation shows parity after model and runtime
  changes, including any quantization; lower cost alone is not sufficient.
- Data residency, contractual control, or provider availability requirements
  outweigh the extra operating burden.

Keep the API choice if traffic is bursty or below break-even, the GPU would be
underused, operations staffing is not available, or provider pricing remains
below the fully loaded self-host cost. Compression and safe public-FAQ caching
would reduce billable API requests/tokens and push the crossover farther out;
cache evidence here is fixture-only and excludes patient-specific answers.

**Next decision evidence:** capture dated routed API prices, real token/retry
distributions, and peak concurrency; run controlled baseline/10x SLO and
quality tests; obtain a region-specific GPU quote and benchmark before revising
the recommendation. Until then, retain API-hosted inference as the economic
default and keep the local deterministic fallback clearly labeled.