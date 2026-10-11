# Two Optimisation Levers: Measurements

Run the fixture scripts from the repository root. Results below were reproduced
in the existing Python 3.14 venv on 2026-10-11. No model provider was called;
API costs are estimates using the rates/retry assumptions in
[`cost/cost_model.md`](../cost/cost_model.md).

| Lever | Before | After | Measured result |
| --- | --- | --- | --- |
| Public FAQ response cache | 8 fixture requests miss; estimated token cost is $0.17901/1k requests ($0.00143208 for this 8-request replay) | 5/8 hits; 3 estimated model requests; $0.06712875/1k ($0.00053703 for this replay) | 62.5% hit rate and estimated token-cost reduction; cache infrastructure cost excluded |
| In-memory batch queue | 7 jobs in 7 one-job groups | 7 jobs in 2 groups at batch-size 4 | 71.4% fewer local work groups; zero provider calls and no provider batch discount claimed |

Reproduce:

```bash
python3 -m levers.cache_hitrate
python3 -m levers.batch_worker --batch-size 4
python3 -m pytest -q tests/test_cost_estimator.py
```

## Quality and limitations

- The cache accepts only three allow-listed public FAQ IDs; it does not cache
	free text, patient-specific prompts, or clinical triage responses. Its TTL is
	300 seconds. The replay returned the exact source fixture for 8/8 requests
	(100% fixture-source agreement), but this is not an independent quality,
	semantic-equivalence, freshness, or clinical-safety evaluation. A source
	update can leave an answer stale until TTL expiry.
- The worker uses an in-memory FIFO queue and a deterministic fixture rule. It
	preserves job order and routes all 3 urgent/review fixtures to
	`human_review`; this checks queue behavior, not model quality. Process loss
	loses queued jobs because no durable broker is configured.
- Group count is not provider API-call count. Jobs are not sent to an external
	Batch API. Per-request token charges do not change just because local work is
	grouped, so no batch dollar savings are claimed.
- No p95 latency, production throughput, or load result is measured. Interactive
	work retains a 2-second p95 target in
	[`batch_vs_interactive.py`](batch_vs_interactive.py); batch work has a
	completion deadline instead. Measure queue wait, execution latency, model
	tokens, retries, cache outcomes, status, and cost tags before production.

Any semantic-cache expansion must be evaluated on a held-out fixture set for
answer equivalence and safety before rollout. Cost reduction alone is not a
quality gate; uncertain clinical cases continue to human review.