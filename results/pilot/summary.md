# Pilot summary

40 Swedish dev prompts, greedy, max 256 new tokens.

| Model | Revision | Swedish rate | 95% CI | Language counts | Hit token limit |
|---|---|---:|---|---|---:|
| qwen2.5-0.5b | `7ae557604a` | 100.0% | 91%-100% | {'sv': 40} | 37 |
| qwen3-0.6b | `c1899de289` | 100.0% | 91%-100% | {'sv': 40} | 17 |
| smollm2-360m | `a10cc1512e` | 85.0% | 71%-93% | {'sv': 34, 'en': 4, 'de': 1, 'nb': 1} | 8 |

**Gate:** GO_SMALL_HEADROOM. Lowest Swedish rate is between 75% and 90%: run the experiment on this model and state in the report that headroom is small (Deviation 2).
Lowest Swedish rate: **smollm2-360m** (85.0%).
