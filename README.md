# API_COST_ESTIMATOR

Cost-optimised deployment study for the AfyaPlus AI API. The capstone compares
managed API spend at baseline and sustained 10x traffic, adds cache and batch
fixtures, and documents deployment controls and the API-vs-self-host trade-off.

## Executive decision

Use the managed model API for the pilot and defer GPU self-hosting. At the
stated assumptions, total TCO is **$5.3790 per 1,000 requests / $537.90 per
month** at 100,000 monthly requests, and **$0.9790 per 1,000 / $979.01 per
month** at a sustained 1,000,000 requests. Token spend is only one part of the
estimate; infrastructure and allocated people/ops are shown separately.

These are scenario estimates, not measured bills or cloud quotes. The
`gpt-4o-mini` token rates are inherited exercise inputs and must be checked
against current OpenRouter pricing before use in a budget. Infrastructure,
labor, retries, and traffic shape are explicit editable assumptions in
[`cost/cost_model.md`](cost/cost_model.md).

## Repository layout

```text
api/                         Unchanged Week 6 FastAPI + Docker spine
cost/cost_model.py           Token-cost arithmetic
cost/sensitivity.py          Baseline, 10x, cache, and token sensitivities
cost/cost_model.md            Assumptions, rates, and cost narrative
deploy/docker-compose.cost.yml
deploy/azure_budget_triage.json
deploy/aws_budget.json
deploy/budget_alert_notes.md
levers/cache_triage.py        TTL cache for allow-listed public FAQ IDs only
levers/cache_hitrate.py       Fixture replay and before/after cost evidence
levers/batch_worker.py        Offline mock batch worker
levers/batch_vs_interactive.py Interactive SLO vs batch completion deadline
levers/measurements.md        Reproducible fixture measurements
memo/api_vs_selfhost.md       Break-even assumptions and decision gates
exec/one_pager.pdf            Executive one-pager
exec/one_pager.md             One-pager source
exec/build_one_pager.py       Rebuild the PDF
```

## Reproduce locally

Python 3.10+ is required. From the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest -q tests/test_cost_estimator.py
python3 -m cost.sensitivity
python3 -m levers.cache_hitrate
python3 -m levers.batch_worker --batch-size 4
python3 exec/build_one_pager.py
```

The API has its own dependencies and instructions in [`api/README.md`](api/README.md).
To validate the cost-labelled local Compose deployment, set a development
`JWT_SECRET` and run:

```bash
export JWT_SECRET='replace-with-a-local-development-secret'
docker compose -f deploy/docker-compose.cost.yml config
docker compose -f deploy/docker-compose.cost.yml up --build
```

## Deployment and cost controls

The local API fallback uses the existing Week 6 JWT-protected FastAPI service,
bound to loopback with CPU/memory limits and cost-identification labels. Azure
and AWS budget files are example alert configurations for a proposed
$1,000/month cap, not deployed budgets. Replace contact placeholders and
confirm scope before applying them. Alerts do not stop spend automatically.

No paid cloud account, Redis, GPU, Kubernetes cluster, live load test, or live
OpenRouter call is claimed. Cache evidence is limited to eight public FAQ
fixtures (5 hits, 62.5%); it must not be generalized to patient-specific
triage. The mock worker groups seven offline jobs into two batches and does not
claim a provider batch discount or production throughput. See the measurements
and decision memo for limitations, SLO gates, security, quotas, cold starts,
observability, retries, and optimization trade-offs.

## Local deployment evidence

On 2026-10-11 the Compose image built successfully; the container became
healthy on `127.0.0.1:8000` with a 1 CPU quota and 512 MiB memory limit. Python
checks returned `GET /health: 200` and an authenticated `POST /agent/ask: 200`
using the local clinic catalog. The endpoint is a deterministic MCP-backed
fallback, not a live OpenRouter model call. Docker labels match the cloud
`CostCenter`, `Environment`, and `Workload` tags. Full commands and response
evidence are in [deploy/budget_alert_notes.md](deploy/budget_alert_notes.md).