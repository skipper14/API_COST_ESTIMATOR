# OpenRouter Rate Snapshot

Retrieved from the public OpenRouter model catalog on **2026-10-11**. This was
a metadata GET only; no key, paid generation, or model inference was used. The
catalog returns `pricing.prompt` and `pricing.completion` in USD per token.

| Model ID in catalog | Input / prompt per 1M tokens | Output / completion per 1M tokens | Other |
| --- | ---: | ---: | --- |
| `openai/gpt-4o-mini` | $0.15 | $0.60 | Cached input: $0.075 / 1M |
| `openai/gpt-4o-mini:batch` | $0.075 | $0.30 | Async batch route; not used by the local fixture worker |
| `openai/gpt-4o` | $2.50 | $10.00 | Standard route |

Source: <https://openrouter.ai/api/v1/models>. Search the response by exact
model `id`; do not infer a batch price by halving the standard route. Prices and
model availability can change, so retrieve a dated snapshot again before a
budget, purchase decision, or external quote. The primary cost model uses the
standard `gpt-4o-mini` route, not cached-input or batch rates.