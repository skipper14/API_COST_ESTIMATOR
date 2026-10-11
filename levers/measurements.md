# Lever Measurements

These are deterministic local fixture results, not production measurements.
Re-run the listed commands from the repository root to reproduce them. Cache
fixtures contain public reference FAQ identifiers only; no patient text or
live model call is involved.

| Lever | Before | After | Evidence / interpretation |
| --- | --- | --- | --- |
| Public FAQ cache | 8 fixture requests, 8 model calls, $0.00143208 estimated token spend | 5 cache hits (62.5%), 3 model calls, $0.00053703 estimated token spend | TTL is 300 seconds; excludes cache infrastructure cost and assumes hits are semantically safe |
| Non-interactive batch | 7 fixture jobs treated as 7 independent queue submissions | 7 jobs grouped into 2 local batches at batch-size 4; zero model calls | Demonstrates split/worker behavior only; no latency, throughput, or provider batch discount claimed |

```bash
python3 -m levers.cache_hitrate
python3 -m levers.batch_worker --batch-size 4
```

The API's interactive path retains a 2-second p95 target in
`levers/batch_vs_interactive.py`; batch jobs use a completion deadline instead
of an interactive latency SLO. The local fixture worker does not yet enqueue
to a broker or call a provider. Before production, instrument request IDs,
model/token usage, cache outcome, retry count, queue wait, execution latency,
status, and cost-center/environment/workload tags. Compare p95 and quality
alongside cost, and fail closed on clinical uncertainty.