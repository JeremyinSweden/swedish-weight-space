# Pilot 2 summary

Dev only. max_new_tokens 512. Loop = a lowercased word 8-gram occurs >= 3 times.
Median tokens = median new tokens of non-looping responses (baseline for the early-stop check).

| Model | Decoding | Set | Loop rate | 95% CI | Hit 512 limit | Median tokens (non-loop) | Math acc |
|---|---|---|---:|---|---:|---:|---:|
| qwen2.5-0.5b | greedy | sv_open | 90% (36/40) | 77%-96% | 78% (31/40) | 216 (n=4) | - |
| qwen2.5-0.5b | greedy | en_open | 22% (9/40) | 12%-38% | 15% (6/40) | 196 (n=31) | - |
| qwen2.5-0.5b | greedy | sv_math | 3% (2/60) | 1%-11% | 2% (1/60) | 23 (n=58) | 23% (14/60) |
| qwen2.5-0.5b | greedy | en_math | 0% (0/60) | 0%-6% | 0% (0/60) | 39 (n=60) | 82% (49/60) |
| qwen2.5-0.5b | recommended | sv_open | 42% (17/40) | 29%-58% | 28% (11/40) | 319 (n=23) | - |
| qwen2.5-0.5b | recommended | en_open | 2% (1/40) | 0%-13% | 2% (1/40) | 273 (n=39) | - |
| qwen2.5-0.5b | recommended | sv_math | 0% (0/60) | 0%-6% | 0% (0/60) | 32 (n=60) | 32% (19/60) |
| qwen2.5-0.5b | recommended | en_math | 0% (0/60) | 0%-6% | 0% (0/60) | 72 (n=60) | 77% (46/60) |
| qwen3-0.6b | greedy | sv_open | 55% (22/40) | 40%-69% | 32% (13/40) | 157 (n=18) | - |
| qwen3-0.6b | greedy | en_open | 0% (0/40) | 0%-9% | 8% (3/40) | 132 (n=40) | - |
| qwen3-0.6b | greedy | sv_math | 2% (1/60) | 0%-9% | 2% (1/60) | 55 (n=59) | 67% (40/60) |
| qwen3-0.6b | greedy | en_math | 0% (0/60) | 0%-6% | 0% (0/60) | 63 (n=60) | 90% (54/60) |
| qwen3-0.6b | recommended | sv_open | 48% (19/40) | 33%-63% | 28% (11/40) | 158 (n=21) | - |
| qwen3-0.6b | recommended | en_open | 0% (0/40) | 0%-9% | 5% (2/40) | 127 (n=40) | - |
| qwen3-0.6b | recommended | sv_math | 0% (0/60) | 0%-6% | 0% (0/60) | 60 (n=60) | 63% (38/60) |
| qwen3-0.6b | recommended | en_math | 0% (0/60) | 0%-6% | 0% (0/60) | 58 (n=60) | 93% (56/60) |

## Math accuracy split by looping (paper-style strata, greedy and recommended)

| Model | Decoding | Set | Acc. when looping | Acc. when not looping |
|---|---|---|---:|---:|
| qwen2.5-0.5b | greedy | sv_math | 0% (0/2) | 24% (14/58) |
| qwen2.5-0.5b | greedy | en_math | n/a | 82% (49/60) |
| qwen2.5-0.5b | recommended | sv_math | n/a | 32% (19/60) |
| qwen2.5-0.5b | recommended | en_math | n/a | 77% (46/60) |
| qwen3-0.6b | greedy | sv_math | 0% (0/1) | 68% (40/59) |
| qwen3-0.6b | greedy | en_math | n/a | 90% (54/60) |
| qwen3-0.6b | recommended | sv_math | n/a | 63% (38/60) |
| qwen3-0.6b | recommended | en_math | n/a | 93% (56/60) |

## P1: Swedish minus English loop rate (greedy, paired, cluster bootstrap 95% CI)

| Model | Prompts | sv - en | 95% CI | >= 20 points? |
|---|---|---:|---|---|
| qwen2.5-0.5b | open | +68 pts | +50 to +82 | yes |
| qwen2.5-0.5b | math | +3 pts | +0 to +8 | no |
| qwen3-0.6b | open | +55 pts | +38 to +71 | yes |
| qwen3-0.6b | math | +2 pts | +0 to +5 | no |

## P2: recommended minus greedy loop rate on Swedish prompts (paired)

| Model | Prompts | rec - greedy | 95% CI | Reduced? | Removed? |
|---|---|---:|---|---|---|
| qwen2.5-0.5b | open | -48 pts | -65 to -30 | yes | no |
| qwen2.5-0.5b | math | -3 pts | -8 to +0 | yes | yes |
| qwen3-0.6b | open | -8 pts | -20 to +5 | yes | no |
| qwen3-0.6b | math | -2 pts | -5 to +0 | yes | yes |

## Gate (sv_open loop rate under greedy >= 40%)

Qwen2.5 rate 90%, Qwen3 rate 55%. Mechanical outcome: **main** (qwen2.5-0.5b). To be confirmed at checkpoint (a2).
