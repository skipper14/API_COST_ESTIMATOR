# AfyaPlus API Cost Model

This is a fixture-driven planning estimate, not a cloud quote or measured
production bill. Run `python3 -m cost.sensitivity` from the repository root to
reproduce the scenarios. Costs are USD for OpenRouter-routed
`openai/gpt-4o-mini`; one logical request makes one model call unless it hits
the modeled cache, and a 2% billed retry allowance is applied to misses.

## Executive view

| Scenario | Volume/month | Model/1k | Infrastructure/1k | People/ops/1k | Total/1k | Monthly total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline, uncached | 100,000 | $0.1790 | $1.2000 | $4.0000 | $5.3790 | $537.90 |
| Sustained 10x, uncached | 1,000,000 | $0.1790 | $0.3000 | $0.5000 | $0.9790 | $979.01 |

The lower spike unit cost is due to spreading the explicitly assumed platform
and staffing allocations over ten times the requests. It is not evidence that
latency or throughput meets an SLO at 10x. The API model's token component is
variable and remains approximately linear with volume.

## Inputs and rates

- Rates used: $0.15 per 1M input tokens and $0.60 per 1M output tokens for
  `gpt-4o-mini`; $2.50 and $10.00 per 1M respectively for `gpt-4o`. These are
  inherited exercise inputs, not independently verified current OpenRouter
  rates. Confirm the routed model price before budgeting or quoting [1].
- Baseline message shape: 450 input tokens and 180 output tokens. The 10x
  scenario holds that average constant; a high-token sensitivity uses 900 input
  and 300 output tokens.
- Retry assumption: 2% of attempts incur one additional billable call with the
  same average token counts. This is a scenario input, not an observed retry
  rate.
- Baseline traffic: 100,000 requests/month. The spike is 1,000,000 requests
  sustained over one month.
- Infrastructure allocation: $120/month baseline and $300/month at the spike,
  including an estimated API host, logs, and network costs. Replace with a
  selected-region cloud quote or measured bill.
- People/ops allocation: $400/month baseline and $500/month at the spike,
  modeled as 8 and 10 hours at $50/hour fully loaded. Replace with actual
  staffing and labor rates.
- Cache hit rate is 0% in the primary estimate. The 30% cache scenarios are
  sensitivities only; evidence comes from public FAQ fixtures and must not be
  generalized to patient-specific triage.
- Taxes, discounts, service credits, one-time engineering, incident response,
  and provider fees beyond the listed token rate are excluded.

The current token shape costs $0.0001755 per first attempt. Applying the 2%
retry allowance gives $0.00017901 per logical request, or $0.17901 per 1,000.
At 100,000 requests, model spend is $17.90/month before infrastructure and ops.

## Trade-offs

The managed API avoids reserved GPU capacity and the associated model serving,
patching, and on-call burden. It exposes the service to provider price changes,
rate limits, and availability. The 10x case therefore requires measured
concurrency, backoff, quotas, latency SLOs, and a queue for non-interactive
work; this cost model alone does not establish capacity.

## Architecture and optimization guardrails

- **Serverless vs containers:** serverless can reduce idle compute cost for
  bursty traffic, but cold starts can breach the interactive 2-second p95
  target. Measure cold and warm latency before choosing it; a small warm
  minimum or the existing container spine may be preferable for steady traffic.
- **Autoscaling and quotas:** scale on concurrency/queue depth with a maximum
  replica count, provider rate limit, and monthly spend alert. Autoscaling
  without a provider quota or concurrency ceiling can amplify a retry storm.
- **Resilience and telemetry:** instrument request ID, route/model, prompt and
  completion tokens, retries, cache outcome, queue wait, latency, status, and
  cost tags. Use capped exponential backoff and a circuit breaker for repeated
  429/5xx or timeout responses; fail closed to the human-review path rather
  than inventing a clinical answer.
- **SLO and quality gate:** interactive requests retain a p95 target of 2,000
  ms. Batch work has a completion deadline instead of the interactive SLO.
  A/B changes to model, prompt compression, cache, or token caps must compare
  cost and latency alongside safety/quality scores; do not promote on cost
  savings alone.
- **Optimization boundary:** prompt compression and output caps can reduce
  billed API tokens and are candidates for fixture-backed A/B tests. The
  sensitivity's 900/300 token case is a token-growth scenario, not a measured
  compression result. Quantization, pruning, and KV-cache tuning belong to a
  self-hosted inference stack; they do not reduce a hosted API's billed token
  count and are not claimed as measured levers here. KV-cache discounts, if
  exposed by a provider, require separate rate verification.
- **Secrets and identity:** keep provider keys and JWT signing secrets outside
  source and images; inject them from a managed secret store or local runtime
  environment. Use least-privilege workload identity for cloud billing and
  budget administration. The current stub Compose deployment uses a runtime
  JWT secret and makes no provider call.
- **Batch split:** retain the interactive path for synchronous user requests;
  send eligible offline work to a throttled queue/provider batch path with a
  deadline. Do not promise a batch price discount until the provider rate is
  verified.

## Rate reference

1. OpenRouter model page: <https://openrouter.ai/openai/gpt-4o-mini>. The page
   identifies the routed model but did not expose a numeric rate in the captured
   documentation. Rates above are inherited from the repository exercise and
   remain unverified assumptions; record a dated pricing capture when refreshed.