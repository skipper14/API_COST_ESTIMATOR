import pytest

from cost.cost_model import cost_per_request
from cost.sensitivity import SCENARIOS, estimate
from levers.batch_worker import FIXTURE_JOBS, process_jobs
from levers.cache_triage import PUBLIC_FAQ, PublicReferenceCache


def test_cost_per_request_uses_per_million_rates() -> None:
    assert cost_per_request(450, 180, "gpt-4o-mini") == pytest.approx(0.0001755)


def test_baseline_and_spike_cost_per_thousand() -> None:
    baseline = estimate(SCENARIOS[0])
    spike = estimate(SCENARIOS[2])

    assert baseline["total_usd_per_1k"] == pytest.approx(5.37901)
    assert spike["total_usd_per_1k"] == pytest.approx(0.97901)
    assert baseline["monthly_total_usd"] == pytest.approx(537.901)
    assert spike["monthly_total_usd"] == pytest.approx(979.01)


def test_sensitivity_rejects_invalid_cache_rate() -> None:
    with pytest.raises(ValueError, match="cache_hit_rate"):
        estimate(SCENARIOS[0].__class__("invalid", 1000, 450, 180, 1.2, 1, 1))


def test_public_reference_cache_expires_and_rejects_free_text() -> None:
    now = [100.0]
    cache = PublicReferenceCache(ttl_seconds=10, clock=lambda: now[0])
    faq_id = "clinic-hours"
    cache.put(faq_id, PUBLIC_FAQ[faq_id])
    assert cache.get(faq_id) == PUBLIC_FAQ[faq_id]

    now[0] += 10
    assert cache.get(faq_id) is None
    with pytest.raises(KeyError, match="allow-listed"):
        cache.put("patient symptoms and phone number", "not cached")


def test_batch_worker_groups_jobs_without_model_calls() -> None:
    results = process_jobs(FIXTURE_JOBS, batch_size=4)

    assert len(results) == 7
    assert {result["batch_number"] for result in results} == {"1", "2"}
    assert results[3]["result"] == "human_review"