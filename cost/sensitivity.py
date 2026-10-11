"""Scenario sensitivity for AfyaPlus triage unit and monthly costs."""

from dataclasses import dataclass

from cost.cost_model import cost_per_request


RETRY_RATE = 0.02
MODEL = "gpt-4o-mini"


@dataclass(frozen=True)
class Scenario:
    name: str
    requests: int
    input_tokens: int
    output_tokens: int
    cache_hit_rate: float
    infrastructure_usd: float
    people_ops_usd: float


SCENARIOS = (
    Scenario("baseline", 100_000, 450, 180, 0.00, 120.00, 400.00),
    Scenario("baseline_cache_30pct", 100_000, 450, 180, 0.30, 120.00, 400.00),
    Scenario("spike_10x", 1_000_000, 450, 180, 0.00, 300.00, 500.00),
    Scenario("spike_10x_cache_30pct", 1_000_000, 450, 180, 0.30, 300.00, 500.00),
    Scenario("spike_10x_high_tokens", 1_000_000, 900, 300, 0.00, 300.00, 500.00),
)


def estimate(scenario: Scenario) -> dict[str, float | int | str]:
    if scenario.requests <= 0:
        raise ValueError("requests must be greater than zero")
    if not 0 <= scenario.cache_hit_rate <= 1:
        raise ValueError("cache_hit_rate must be between zero and one")

    uncached_model_cost = cost_per_request(
        scenario.input_tokens, scenario.output_tokens, MODEL
    )
    model_spend = (
        scenario.requests
        * uncached_model_cost
        * (1 + RETRY_RATE)
        * (1 - scenario.cache_hit_rate)
    )
    monthly_total = (
        model_spend + scenario.infrastructure_usd + scenario.people_ops_usd
    )
    return {
        "scenario": scenario.name,
        "requests_per_month": scenario.requests,
        "input_tokens": scenario.input_tokens,
        "output_tokens": scenario.output_tokens,
        "cache_hit_rate": scenario.cache_hit_rate,
        "model_usd_per_1k": model_spend * 1_000 / scenario.requests,
        "infrastructure_usd_per_1k": scenario.infrastructure_usd * 1_000 / scenario.requests,
        "people_ops_usd_per_1k": scenario.people_ops_usd * 1_000 / scenario.requests,
        "total_usd_per_1k": monthly_total * 1_000 / scenario.requests,
        "monthly_total_usd": monthly_total,
    }


def main() -> None:
    print(
        "scenario,requests/month,input_tokens,output_tokens,cache_hit_rate,"
        "model/1k,infra/1k,people-ops/1k,total/1k,monthly-total"
    )
    for scenario in SCENARIOS:
        result = estimate(scenario)
        print(
            f"{result['scenario']},{result['requests_per_month']},"
            f"{result['input_tokens']},{result['output_tokens']},"
            f"{result['cache_hit_rate']:.0%},{result['model_usd_per_1k']:.4f},"
            f"{result['infrastructure_usd_per_1k']:.4f},"
            f"{result['people_ops_usd_per_1k']:.4f},"
            f"{result['total_usd_per_1k']:.4f},{result['monthly_total_usd']:.2f}"
        )


if __name__ == "__main__":
    main()