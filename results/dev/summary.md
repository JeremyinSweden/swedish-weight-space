# Dev selection (Step 5)

C0 dev: sv_open loops 90%, en_open loops 22%, short (<30 tokens) sv 0% / en 0%

| Config | Layers | k | alpha | Frobenius norm | sv_open loop | en_open loop | en <= C0? | Early-stop | Eligible |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| default | [15, 19] | 64 | 1.0 | 0.777 | 92% | 30% | no | pass | no |
| g1_L15-19_k64_a2 | [15, 19] | 64 | 2.0 | 1.555 | 95% | 20% | yes | pass | yes |
| g2_L15-19_k256_a1 | [15, 19] | 256 | 1.0 | 1.022 | 95% | 20% | yes | pass | yes |
| g3_L15-19_k256_a2 | [15, 19] | 256 | 2.0 | 2.043 | 92% | 22% | yes | pass | yes |
| g4_top2_k64_a2 | [15, 16] | 64 | 2.0 | 1.610 | 92% | 18% | yes | pass | yes |
| g5_top2_k256_a2 | [15, 16] | 256 | 2.0 | 2.053 | 95% | 12% | yes | pass | yes |
| g6_L15-19_k1024_a1 | [15, 19] | 1024 | 1.0 | 1.247 | 92% | 18% | yes | pass | yes |

| Steering | alpha_s | sv_open loop | en_open loop | Early-stop | Eligible |
|---|---:|---:|---:|---|---|
| C2_a1 | 1.0 | 50% | 25% | pass | no |
| C2_a2 | 2.0 | 38% | 40% | FAIL | no |

**Selected C3:** g6_L15-19_k1024_a1 (layers [15, 19], k=1024, alpha=1.0)
**Selected C2:** alpha_s=1.0 at layers [15, 19]
Dev feedback passes: 10. Frozen config: configs/frozen.json
