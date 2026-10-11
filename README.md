# Week 7, Cost-Optimised AI Deployment

## Overview

This estimates managed-API costs for AfyaPlus text intake at 100,000
requests/month and a sustained 10x scenario of 1,000,000 requests/month. The
estimated fully allocated cost is **$5.3790 per 1,000 requests at baseline**
and **$0.9790 per 1,000 at 10x**; token, infrastructure, and people/operations
costs are separated. These are planning estimates, not bills or capacity tests.

## Cost model

See the [cost model](cost/cost_model.md) for calculations and sensitivity
scenarios, and the [dated provider-rate snapshot](cost/provider_rate_snapshot.md).
The standard `gpt-4o-mini` rates were verified on 2026-10-11; refresh them
before budgeting.
Infrastructure and labor remain explicit planning allocations, not cloud quotes.

## Deploy & budgets

Local run: install the API and capstone packages, set a development `JWT_SECRET`,
then start Compose. The service binds to loopback with 1 CPU and 512 MiB limits.
FinOps labels are `CostCenter=afyaplus-ai-platform`,
`Environment=capstone`, and `Workload=triage-api`.

```bash
python3 -m pip install -r api/requirements.txt pandas reportlab
export JWT_SECRET='replace-with-a-local-development-secret'
docker compose -f deploy/docker-compose.cost.yml up --build
```

The [Azure](deploy/azure_budget_triage.json) and
[AWS](deploy/aws_budget.json) examples set a **$1,000 monthly budget** with
notices at $800 actual, $1,000 actual, and $1,000 forecast. These are
config-as-submitted, not deployed cloud budgets; alerts notify but do not stop
spend. [Deployment notes](deploy/budget_alert_notes.md) contain local run
evidence and scope/secret guidance.

## Levers implemented

1. [Public FAQ TTL cache](levers/cache_triage.py): on 8 public fixture IDs,
	 5 HITs / 3 MISSes (62.5% hit rate); estimated token cost changes from
	 $0.17901 to $0.06713 per 1,000 requests. All 8 answers match their exact
	 source fixtures, which is not independent clinical-quality evidence.
2. [Offline FIFO batch queue](levers/batch_worker.py): 7 fixture jobs move from
	 7 one-job groups to 2 groups (71.4% fewer groups). No provider calls,
	 provider discount, p95, or throughput gain is claimed.

Detailed [before/after measurements and quality caveats](levers/measurements.md)
include cache MISS/HIT output and replay commands. The cache only accepts
allow-listed public FAQ IDs; no patient-specific answers are cached. The
in-memory queue is not durable across process failure.

## API vs self-host memo

See the [API vs self-host memo](memo/api_vs_selfhost.md). Decision summary:

- Managed API is recommended for the pilot; at the modeled rates it costs
	$179.01/month in tokens at 1M requests, before the separately allocated API
	infrastructure and people/ops.
- A hypothetical $2,730/month self-host serving floor crosses API token spend
	near 15.25M requests/month; omitted GPU capacity and operations costs push
	that threshold higher.
- No GPU or open model was run. Treat break-even as a screening estimate until
	provider prices, workload throughput, quality, and a regional GPU quote are
	measured.

## Executive one-pager

Read the one-page [executive brief PDF](exec/one_pager.pdf). Recommendation:
**conditional GO** for a small,
human-reviewed pilot. **NO-GO** for autonomous clinical use or a production 10x
launch until the $1,000/month budget controls are active, current model rates
are verified, interactive p95 is below 2 seconds under controlled load, safety
quality passes, and the local fallback is available. p95 means 95 out of 100
requests finish within the stated time.

## Fallbacks declared

- [x] Redis unavailable/not used; use in-memory dictionary cache with 300-second TTL.
- [x] GPU unavailable/not used; no quantization smoke test claimed.
- [x] Paid cloud unavailable/not used; local Compose plus Azure/AWS budget configs.
- [x] Live model API/load tests not run; deterministic fixtures avoid paid calls.

## Checklist

- [x] $/1k at baseline and stated 10x scenario: [cost model](cost/cost_model.md).
- [x] Budget threshold and local run evidence: [deployment notes](deploy/budget_alert_notes.md).
- [x] Two implemented levers with before/after metrics: [measurements](levers/measurements.md).
- [x] Heuristic/cache quality limits and fallback status stated honestly.
- [ ] Executive language reviewed by a non-author classmate; review is still pending.

## Full-Marks Readiness

Local fallback evidence is reproducible, but these items still limit a full
production-evidence score:

- **Deployment/budgets:** Compose was built and health-checked locally. Azure
	and AWS budgets are config-as-submitted only; no console deployment or alert
	delivery was observed. The no-paid-cloud fallback is documented.
- **Infrastructure and people costs:** the $120/$300 monthly hosting allocations
	and $50/hour operations rate are disclosed scenarios, not sourced quotes.
	Replace them with a region-specific cloud calculator export, log/egress
	estimate, and finance-approved loaded labor rate/hours.
- **Model service:** the runnable agent is deterministic and does not call
	OpenRouter. Do not describe it as live LLM inference. A bounded, token-capped
	smoke request is still needed if model credits are available.
- **Scale/SLO:** no production-model or 10x load test measured p95. Run a
	controlled local load against the API wrapper and verify provider quotas,
	response time, and quality before claiming 10x readiness.
- **Self-host:** GPU rental and operations costs are explicit sensitivities,
	not quotes or a GPU benchmark. Get a regional quote and capacity/quality test
	before using the crossover for procurement.
- **Review:** a non-author classmate review is still pending; leave its checklist
	box unchecked until someone completes it.

## Reproduce

Run from the repository root using Python 3.10+:

```bash
python3 -m pytest -q tests/test_cost_estimator.py
python3 -m cost.sensitivity
python3 -m levers.cache_hitrate
python3 -m levers.batch_worker --batch-size 4
```
