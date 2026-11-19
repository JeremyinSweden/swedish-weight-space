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

## Pilot 2

(To be filled in.)
