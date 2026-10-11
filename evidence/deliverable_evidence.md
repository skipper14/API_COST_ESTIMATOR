# Week 7 Terminal Evidence

Observed local runs on 2026-10-11. Commands were run from the repository root
in the existing Python 3.14 `.venv2` where noted. Fixtures do not call an AI
provider. Cloud budget files are examples; no paid cloud account was used.

## Cache MISS/HIT and cost challenge

Command: `python -m levers.cache_hitrate`

```text
request,faq_id,cache,source_match
1,malaria-prevention,MISS,true
2,clinic-hours,MISS,true
3,malaria-prevention,HIT,true
4,vaccine-schedule,MISS,true
5,clinic-hours,HIT,true
6,malaria-prevention,HIT,true
7,clinic-hours,HIT,true
8,malaria-prevention,HIT,true
fixture_requests,8
estimated_model_requests_before,8
cache_hits,5
estimated_model_requests_after,3
hit_rate,62.5%
fixture_source_matches,8
fixture_source_agreement,100.0%
model_cost_before_usd_per_1k,0.17901000
model_cost_after_usd_per_1k,0.06712875
```

These are estimated token charges using declared rates/retry assumptions, not
actual API calls or a quality evaluation. Exact fixture-source agreement does
not establish clinical correctness.

## Batch fixture

Command: `python -m levers.batch_worker --batch-size 4`

```text
jobs=7 groups_before=7 groups_after=2 grouping_reduction=71.4% mode=local-fixture-no-provider-calls
```

All seven jobs were returned in original order; three urgent/review fixture
jobs were routed to human review. Group reduction is local queue grouping only,
not reduced provider billing or measured throughput.

## Budget configuration

Validated both JSON documents with `python -m json.tool`. A Python assertion
against the files reported:

```text
Azure cap USD 1000; AWS cap USD 1000; alerts 80/100 actual + 100 forecast
```

This confirms submitted configuration values only; no cloud alert was deployed
or triggered. See [`../deploy/budget_alert_notes.md`](../deploy/budget_alert_notes.md)
for threshold values, contact placeholders, and operator notes.

## Local API deployment

Run path (use a throwaway development JWT value; never commit it):

```bash
export JWT_SECRET='replace-with-a-local-development-secret'
docker compose -p afya-cost -f deploy/docker-compose.cost.yml up --detach --build
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health').read().decode())"
docker compose -p afya-cost -f deploy/docker-compose.cost.yml down
```

Observed in the local Docker run:

```text
image build: succeeded
container: healthy at 127.0.0.1:8000
health: {"service":"AfyaPlus E-commerce Fulfilment API","version":"1.0.0","status":"ok"}
authenticated POST /agent/ask: HTTP 200, grounded fixture response
cpu quota: 1 CPU
memory limit: 536870912 bytes
cost tags: CostCenter=afyaplus-ai-platform, Environment=capstone, Workload=triage-api
```

The agent endpoint is deterministic and backed by the local clinic catalog; it
is not live LLM deployment evidence. Full deployment notes:
[`../deploy/budget_alert_notes.md`](../deploy/budget_alert_notes.md).