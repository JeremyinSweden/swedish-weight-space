# 3. Lab notes

Running record of what was run, what was seen, and what was decided. Raw outputs are in `results/`.
These notes feed the research note; they are kept as written at the time.

## 2026-11-19: Pilot 1 (precondition check for language confusion)

**Setup.** 40 `sv_open` dev prompts; greedy decoding, `repetition_penalty=1.0`, 256 new tokens; language ID with
`lingua` restricted to sv/en/nb/nn/da/de, responses under 20 characters counted as failures.
Outputs: `results/pilot/summary.json`, `summary.md`, `hand_check.md`, `*_responses.jsonl`.

| Model | Revision | lingua "Swedish" rate | 95% CI | Hit 256-token limit | Repeated 8-gram | Readable (hand check, 10 Swedish-labelled) |
|---|---|---:|---|---:|---:|---:|
| Qwen2.5-0.5B-Instruct | `7ae55760` | 100% | 91-100% | 37/40 | 39/40 | 0/10 |
| Qwen3-0.6B (thinking off) | `c1899de2` | 100% | 91-100% | 17/40 | 31/40 | at most 1/10 |
| SmolLM2-360M-Instruct | `a10cc151` | 85% | 71-93% | 8/40 | 15/40 | 0/10 |

No Chinese characters in any response.

**Observations.**
1. **The primary metric is invalid at this scale.** lingua labels a response as Swedish if its words are Swedish.
   Prompt echoes (SmolLM2 repeats the prompt word for word in 5 of the 10 checked answers) and loops of broken Swedish
   ("Detta är en speciellt ordning av ord som är en ordning av ord...") both count as Swedish. A 100% "Swedish rate"
   here does not mean the model answers in Swedish in any useful sense.
2. **The failure the hypothesis needs is absent.** No model shows "writes Swedish well but picks English". The six
   non-Swedish SmolLM2 answers are off-topic English, broken German, or Dutch-like gibberish (lingua has no Dutch, so it
   reported one as Norwegian). These are comprehension failures, not wrong language choices.
3. **This is the paper's Gemma case, in Swedish.** The models lack the ability; there is no hidden ability blocked by a
   removable failure. The paper's own evidence predicts that a weight edit cannot help here.
4. **The paper's own failure does appear.** Qwen2.5-0.5B loops on almost every Swedish prompt under greedy decoding.
   Open question: how much of this is caused by greedy decoding with no repetition penalty (Qwen recommends sampling with
   `repetition_penalty=1.05`)?
5. Hand-check method: the author read the answers with the help of machine translation; Claude (in a separate chat)
   judged them independently and agreed.

**Decision.** Pre-registered rule: SmolLM2 fails readability; both Qwen models are above 90%, so the rule says switch to
Scandinavian leakage. That target cannot be measured on incoherent text either. New target: looping in Swedish
generation, with a second pilot to check whether loops survive recommended decoding settings. Recorded as Deviation 4 in
`docs/02_hypothesis.md` before any edit or test-set run.

**Lesson for SE.LLMA (for the report).** Before applying a weight-editing method, check that the target model has the
ability the edit is supposed to release, and validate the behavioural metric on real outputs. Both checks were cheap
here (about 5 minutes of compute) and changed the study.

## 2026-11-19: Pilot 2 (Deviation 4: loop precondition and decoding check)

**Setup.** Dev data only: 40 `sv_open`, the 40 parallel `en_open`, 60 `sv_math`, 60 `en_math`. Same pinned revisions
as pilot 1. `max_new_tokens` 512. Two decodings: (i) greedy, `repetition_penalty=1.0`; (ii) recommended settings
(Qwen2.5: T=0.7, top_p=0.8, top_k=20, `repetition_penalty=1.05`; Qwen3 non-thinking: T=0.7, top_p=0.8, top_k=20,
min_p=0, `repetition_penalty=1.0`), fixed seed per cell. Loop = a lowercased word 8-gram occurs at least 3 times.
Script: `scripts/03_pilot2.py`, config `configs/pilot2.json`. Outputs: `results/pilot2/summary.json`, `summary.md`,
`samples.md`, one JSONL per cell.

| Model | Decoding | Set | Loop rate | 95% CI | Hit 512 limit | Median tokens, non-loop (n) | Math acc |
|---|---|---|---:|---|---:|---:|---:|
| Qwen2.5-0.5B | greedy | sv_open | 90% (36/40) | 77-96% | 78% (31/40) | 216 (4) | - |
| Qwen2.5-0.5B | greedy | en_open | 22% (9/40) | 12-38% | 15% (6/40) | 196 (31) | - |
| Qwen2.5-0.5B | greedy | sv_math | 3% (2/60) | 1-11% | 2% (1/60) | 23 (58) | 23% (14/60) |
| Qwen2.5-0.5B | greedy | en_math | 0% (0/60) | 0-6% | 0% (0/60) | 39 (60) | 82% (49/60) |
| Qwen2.5-0.5B | recommended | sv_open | 42% (17/40) | 29-58% | 28% (11/40) | 319 (23) | - |
| Qwen2.5-0.5B | recommended | en_open | 2% (1/40) | 0-13% | 2% (1/40) | 273 (39) | - |
| Qwen2.5-0.5B | recommended | sv_math | 0% (0/60) | 0-6% | 0% (0/60) | 32 (60) | 32% (19/60) |
| Qwen2.5-0.5B | recommended | en_math | 0% (0/60) | 0-6% | 0% (0/60) | 72 (60) | 77% (46/60) |
| Qwen3-0.6B | greedy | sv_open | 55% (22/40) | 40-69% | 32% (13/40) | 157 (18) | - |
| Qwen3-0.6B | greedy | en_open | 0% (0/40) | 0-9% | 8% (3/40) | 132 (40) | - |
| Qwen3-0.6B | greedy | sv_math | 2% (1/60) | 0-9% | 2% (1/60) | 55 (59) | 67% (40/60) |
| Qwen3-0.6B | greedy | en_math | 0% (0/60) | 0-6% | 0% (0/60) | 63 (60) | 90% (54/60) |
| Qwen3-0.6B | recommended | sv_open | 48% (19/40) | 33-63% | 28% (11/40) | 158 (21) | - |
| Qwen3-0.6B | recommended | en_open | 0% (0/40) | 0-9% | 5% (2/40) | 127 (40) | - |
| Qwen3-0.6B | recommended | sv_math | 0% (0/60) | 0-6% | 0% (0/60) | 60 (60) | 63% (38/60) |
| Qwen3-0.6B | recommended | en_math | 0% (0/60) | 0-6% | 0% (0/60) | 58 (60) | 93% (56/60) |

Paired differences (cluster bootstrap by topic for open prompts, 2000 resamples, 95% CI):

| Check | Model | Prompts | Difference | 95% CI |
|---|---|---|---:|---|
| P1: sv minus en loop rate, greedy | Qwen2.5 | open | +68 pts | +50 to +82 |
| | Qwen2.5 | math | +3 pts | +0 to +8 |
| | Qwen3 | open | +55 pts | +38 to +71 |
| | Qwen3 | math | +2 pts | +0 to +5 |
| P2: recommended minus greedy, Swedish | Qwen2.5 | open | -48 pts | -65 to -30 |
| | Qwen2.5 | math | -3 pts | -8 to 0 |
| | Qwen3 | open | -8 pts | -20 to +5 |
| | Qwen3 | math | -2 pts | -5 to 0 |

**Gate (as specified).** Qwen2.5 Swedish loop rate under greedy: 90% (threshold 40%). Mechanical outcome: Qwen2.5-0.5B.
Interpretation used by the script: "Swedish loop rate" = `sv_open` loop rate; `sv_math` is reported but not used for
the gate. To confirm at checkpoint (a2).

**Observations (numbers only, no decision).**
1. **P1 holds on open prompts, not on math.** Swedish open prompts loop far more than English ones in both models
   (+68 and +55 points). On math prompts, loops are nearly absent in both languages (at most 2/60).
2. **P2 holds for Qwen2.5 on open prompts.** Recommended settings cut Swedish loops from 90% to 42% but do not remove
   them. For Qwen3 the change is small (55% to 48%) and the CI includes 0. On math there was almost nothing to reduce.
   The script's "reduced" flag only means the difference is below 0; it is not a significance test.
3. **Swedish math is weak, and loops do not explain it.** Qwen2.5 greedy: 23% in Swedish vs 82% in English on the same
   problems. Only 2 of 60 Swedish math answers loop, so the gap sits in non-looping answers (24% accuracy). Qwen3:
   67% vs 90%. Paper-style rescue strata on `sv_math` have almost no looping items to rescue (2 for Qwen2.5, 1 for
   Qwen3 under greedy).
4. **Early-stop baseline is thin for the main cell.** Under greedy, only 4 of 40 Qwen2.5 `sv_open` answers do not loop,
   so the C0 median length of non-looping answers (216 tokens) rests on 4 responses.
5. **English loops exist too.** Qwen2.5 greedy loops on 22% of English open prompts (9/40).
6. **Non-looping Swedish answers are still mostly incoherent** (see `samples.md`), for example repeated words inside
   otherwise non-looping lists ("försvar, försvar, och försvar") and wrong content (allemansrätten described as a
   linguistic convention).
7. **Recommended-settings source.** The Qwen2.5 repo's own `generation_config.json` uses `repetition_penalty=1.1`; the
   pre-registered spec (and this run) used 1.05. Qwen3's repo defaults are its thinking-mode values (T=0.6, top_p=0.95);
   this run used the model card's non-thinking values. Repo defaults are recorded in
   `results/pilot2/repo_generation_defaults.json`.
8. **Feedback passes so far** (`results/feedback_log.jsonl`): pilot 1 was started four times for the two Qwen models
   (disk-space failures and a re-run after a restart) and once for SmolLM2: 9 passes of 40 prompts. Pilot 2: 4 passes
   of 200 prompts (2 models x 2 decodings). None used test data.
9. **Generation speed on the M1 Pro** (float32, MPS, batch size 16; computed from file timestamps, so the first cell
   per model includes model loading). A batch keeps running until its longest response stops, and looping responses
   run to the limit, so wall time is set by batch steps, not by useful tokens.

   | Model | Batch steps per second | Generated tokens per second | Seconds per prompt, open (512 limit) | Seconds per prompt, math | Total for 400 prompts |
   |---|---:|---:|---:|---:|---:|
   | Qwen2.5-0.5B | 14-18 | 124 (average) | 2.2-2.6 | 0.7-0.9 | 9.7 min |
   | Qwen3-0.6B | 8-10 | 61 (average) | 3.8-4.3 | 0.6-1.4 | 14.4 min |

   Planning estimate for one Qwen2.5 condition on the full test set with one decoding (120 `sv_open` + 120 `en_open` +
   100 `sv_math` + 100 `en_math`, 512 tokens): about 11 minutes (open sets about 4-5 min each, math about 1.5 min each).
   Perplexity on `sv_ref`/`en_ref` is teacher-forced and takes seconds.
