"""Replay public FAQ fixtures to measure cache hits without model calls."""

from cost.cost_model import cost_per_request
from levers.cache_triage import PUBLIC_FAQ, PublicReferenceCache


FIXTURE_QUERIES = (
    "malaria-prevention",
    "clinic-hours",
    "malaria-prevention",
    "vaccine-schedule",
    "clinic-hours",
    "malaria-prevention",
    "clinic-hours",
    "malaria-prevention",
)
RETRY_RATE = 0.02


def replay() -> dict[str, float | int]:
    cache = PublicReferenceCache(ttl_seconds=300)
    uncached_requests = 0
    for faq_id in FIXTURE_QUERIES:
        answer = cache.get(faq_id)
        if answer is None:
            uncached_requests += 1
            cache.put(faq_id, PUBLIC_FAQ[faq_id])

    before_cost = len(FIXTURE_QUERIES) * cost_per_request(450, 180, "gpt-4o-mini")
    after_cost = uncached_requests * cost_per_request(450, 180, "gpt-4o-mini")
    before_cost *= 1 + RETRY_RATE
    after_cost *= 1 + RETRY_RATE
    return {
        "fixture_requests": len(FIXTURE_QUERIES),
        "model_calls_before": len(FIXTURE_QUERIES),
        "cache_hits": cache.hits,
        "model_calls_after": uncached_requests,
        "hit_rate": cache.hits / len(FIXTURE_QUERIES),
        "model_cost_before_usd": before_cost,
        "model_cost_after_usd": after_cost,
    }


def main() -> None:
    result = replay()
    print("metric,value")
    for name, value in result.items():
        if name.endswith("_usd"):
            print(f"{name},{value:.8f}")
        elif name == "hit_rate":
            print(f"{name},{value:.1%}")
        else:
            print(f"{name},{value}")


if __name__ == "__main__":
    main()