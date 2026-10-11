# Managed API vs Self-Hosted Model

## Recommendation

Keep the managed API for the capstone and defer self-hosting. At 1,000,000
monthly requests, the modeled API token spend is about **$179/month** at the
stated 450 input / 180 output token shape, including a 2% retry allowance. The
full scenario TCO is **$979.01/month** after the explicit $300 infrastructure
and $500 people/ops allocations. Those rates and allocations are planning
inputs, not a current provider quote or a measured bill.

## Break-even illustration

The break-even below compares only variable model API spend with incremental
self-hosted GPU and model operations. Shared API hosting, data, network,
security, and product costs are excluded from both sides.

| Input | Assumption |
| --- | ---: |
| API token cost per logical request, retries included | $0.00017901 |
| Self-host GPU rental | $1/hour x 730 hours = $730/month |
| Self-host model operations | 40 hours/month x $50/hour = $2,000/month |
| Self-host incremental monthly cost | $2,730/month |
| Simple break-even against API token spend | about 15.25 million requests/month |

Formula: `(GPU monthly rental + self-host model operations) / API token cost
per request`. The $1/hour GPU and 40 staff hours are explicit sensitivity
assumptions, not cloud prices, capacity benchmarks, or staffing commitments.
The GPU estimate assumes sufficient utilization and does not include redundant
capacity, storage, monitoring, networking, or serving engineering. Real
self-host costs can therefore be higher. GPU capacity and quality were not
measured in this capstone.

At 1M monthly requests, API token spend is well below the illustrative $2,730
self-host increment. The managed path also avoids model deployment and GPU
operations; in exchange it has variable token spend, provider quota/availability
risk, and exposure to rate changes. A measured GPU throughput curve and a
verified provider rate are required before treating the break-even as a
procurement decision.

## Decision gates

- Reconfirm current OpenRouter route pricing and record the date/source.
- Benchmark p50/p95 latency, throughput, error rate, and quality at baseline
  and controlled 10x traffic; set concurrency and spend ceilings first.
- Count staff time, GPU utilization, replicas, storage, and serving operations
  in any self-host comparison.
- Keep interactive triage behind its latency SLO; move eligible noninteractive
  workloads to a throttled queue or provider batch endpoint.
- Do not cache patient-specific answers. The cache evidence is limited to
  allow-listed public FAQ fixture identifiers.