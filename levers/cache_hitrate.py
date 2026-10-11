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
    fixture_matches = 0
    for faq_id in FIXTURE_QUERIES:
        answer = cache.get(faq_id)
        if answer is None:
            uncached_requests += 1
            answer = PUBLIC_FAQ[faq_id]
            cache.put(faq_id, answer)
        if answer == PUBLIC_FAQ[faq_id]:
            fixture_matches += 1

    expected_request_cost = cost_per_request(450, 180, "gpt-4o-mini")
    before_cost = len(FIXTURE_QUERIES) * expected_request_cost
    after_cost = uncached_requests * expected_request_cost
    before_cost *= 1 + RETRY_RATE
    after_cost *= 1 + RETRY_RATE
    return {
        "fixture_requests": len(FIXTURE_QUERIES),
        "estimated_model_requests_before": len(FIXTURE_QUERIES),
        "cache_hits": cache.hits,
        "estimated_model_requests_after": uncached_requests,
        "hit_rate": cache.hits / len(FIXTURE_QUERIES),
        "fixture_source_matches": fixture_matches,
        "fixture_source_agreement": fixture_matches / len(FIXTURE_QUERIES),
        "model_cost_before_usd": before_cost,
        "model_cost_after_usd": after_cost,
        "model_cost_before_usd_per_1k": before_cost * 1_000 / len(FIXTURE_QUERIES),
        "model_cost_after_usd_per_1k": after_cost * 1_000 / len(FIXTURE_QUERIES),
    }


def main() -> None:
    result = replay()
    print("metric,value")
    for name, value in result.items():
        if name.endswith("_usd") or name.endswith("_usd_per_1k"):
            print(f"{name},{value:.8f}")
        elif name.endswith("_rate") or name.endswith("_agreement"):
            print(f"{name},{value:.1%}")
        else:
            print(f"{name},{value}")


if __name__ == "__main__":
    main()