# 2. Hypothesis and pre-registered evaluation plan

Written before any model was run. Thresholds and splits below are fixed now; anything changed later is listed
in the "Deviations" section at the end, with the reason.

## 2.1 Question

> When a small multilingual instruct model answers Swedish prompts in another language, can a sparse weight edit of
> the same form as the paper's Qwen patch make it answer in Swedish, without regressions, and is that a removed
> failure or a new capability? Where does the information for the edit come from: the weights alone, or forward
> passes and feedback?

## 2.2 Why it matters

- **It is the closest Swedish analogue to the paper's one strong LLM result.** The Qwen gain came from removing a
  failure (looping) that hid an existing ability. Language confusion has the same shape: the model can often write
  Swedish, but it defaults to English. If weight edits help Swedish models anywhere, it should be here.
- **It is a real problem for Swedish products.** Small multilingual models often reply in English to Swedish users, or
  mix in Norwegian and Danish, which a Swedish user notices immediately.
- **It has cheap, strong alternatives.** A system prompt ("Svara alltid på svenska") or an inference-time steering vector
  may solve the same problem. A weight edit is only worth investigating further if it beats or complements these, or
  if it has a practical advantage (an ordinary checkpoint, no prompt overhead, no inference code).
- **It lets me test the distinction the assignment highlights.** I can build the edit direction in three ways that use
  increasing amounts of model feedback (see 2.4) and measure how much each step adds.

## 2.3 Hypotheses

- **H1 (targeted edit works).** A rank-1 edit to a few MLP output columns, along a "response language" direction,
  raises the share of Swedish responses to held-out Swedish prompts well above the unedited model and above a
  norm-matched random edit of the same columns.
- **H2 (no collateral damage).** The same edit does not make the model answer English prompts in Swedish, and does not
  meaningfully hurt general ability (task accuracy, perplexity, degeneration).
- **H3 (failure removal, not new capability).** On checkable questions asked in Swedish, accuracy is about the same
  before and after the edit, and Swedish perplexity on reference text does not improve. The edit changes *which
  language* the model uses, not *how well* it can use Swedish.
- **H4 (where the information comes from).** A direction computed from activations (forward passes) works better than
  a direction computed from the weights alone (embedding matrix), and selecting layer and strength with dev-set
  feedback matters more than either.

## 2.4 Methods compared

| ID | Condition | Uses forward passes? | Changes weights? |
|---|---|---|---|
| C0 | Unedited model, default chat template | - | no |
| C1 | Prompting: Swedish system prompt "Svara alltid på svenska." | - | no |
| C2 | Inference-time steering: add the activation direction to the residual stream | yes (to build) | no |
| C3 | **Weight edit, activation direction** (the paper's edit form) | yes (to build and select) | yes |
| C4 | **Weight edit, weights-only direction** (from the tied embedding / unembedding matrix: Swedish-specific tokens minus English tokens; no forward pass used to build it) | only for selection | yes |
| C5 | Random edit: same layers, same columns, same per-column change norm as C3, random direction (5 seeds) | - | yes |
| C6 | C1 + C3 combined (does the edit add anything on top of prompting?) | yes | yes |
| C7 (stretch) | Small LoRA fine-tune on Swedish chat data | yes | yes |

**Edit family** (fixed now; the free parameters are selected on dev only):
for a unit direction `u` in the residual stream (pointing from Swedish toward English activations) and a layer
`l`, pick the `k` columns of the MLP down-projection `W_down[l]` whose writes align most with `u`, and set
`W'[:, S] = W[:, S] - alpha * u (u^T W[:, S])`. Free parameters: layers, `k`, `alpha`. This mirrors the p50c edit
(64 columns per layer, two layers). The steering condition C2 uses the same `u` as a fixed vector added at every token.

**Feedback budget.** Every evaluation pass used for selection is logged with its purpose. I report how many passes each
method used, so "weights only" vs "feedback-selected" is a measured quantity, not a label.

**Adaptation from the paper.** I cannot afford a GPT-6 Astra agent loop (the paper's 50-pass run took 20 hours at
maximum reasoning effort). I replace the LLM search policy with a transparent scripted procedure. This tests whether
the *edit form* the LLM found transfers to a Swedish failure, and where the information comes from. It does not test
whether an LLM can find the edit on its own; that is listed as a next experiment.

## 2.5 Model choice (pilot gate)

The Gemma follow-up shows that the method has nothing to work on when the failure is absent. So the model is chosen by a
pilot, under a rule fixed now:

- Candidates (all Apache 2.0): `Qwen/Qwen2.5-0.5B-Instruct`, `Qwen/Qwen3-0.6B` (thinking off),
  `HuggingFaceTB/SmolLM2-360M-Instruct`.
- Pilot set: 40 dev Swedish prompts, greedy decoding.
- Pick the model with the lowest Swedish response rate, provided that its Swedish answers are at least readable
  (I read 10 by hand). Gate: Swedish response rate at most 75%.
- If every candidate is above 90%, the failure does not exist at this scale. I report that as a finding and switch
  the target to Scandinavian leakage (Norwegian/Danish words in Swedish answers).

## 2.6 Data and splits

All prompts are synthetic, generated with a frontier model and spot-checked by me, so they can be shared freely.

| Set | Use | Size |
|---|---|---|
| `sv_open` / `en_open` | Open-ended chat prompts in Swedish / English (parallel) | 80 dev + 120 test each |
| `sv_math` / `en_math` | Short word problems with a numeric answer (checkable in any language) | 60 dev + 100 test each |
| `sv_ref` / `en_ref` | Short reference paragraphs for perplexity (teacher-forced, no generation) | 50 test each |
| `contrast` | Paired sv/en texts used to compute directions | separate from both dev and test |

Directions are built only from `contrast`. Layers, `k` and `alpha` are chosen only on dev. Test is run once per
condition at the end, after the configuration is frozen (the frozen config file is committed before the test run).

## 2.7 Metrics

- **Primary: Swedish response rate** on `sv_open` test = share of responses classified as Swedish by `lingua`
  (restricted to sv, en, nb, nn, da, de; responses under 20 characters counted as failures).
- **Regressions:**
  - R1: English response rate on `en_open` test (should stay near 100%).
  - R2: accuracy on `sv_math` and `en_math` (numeric answer extracted regardless of language).
  - R3: perplexity on `sv_ref` and `en_ref`.
  - R4: degeneration: share of responses with a repeated 8-gram, mean distinct-2.
- **Examples:** 5 before/after pairs per condition in the report, chosen by a fixed random seed, not cherry-picked.
- **Statistics:** greedy decoding as the primary setting, plus 3 sampling seeds (temperature 0.7). Paired bootstrap 95%
  CIs for differences between conditions; McNemar's test for paired binary outcomes.

## 2.8 What would support or challenge each hypothesis (decided now)

| Hypothesis | Supported if | Challenged if |
|---|---|---|
| H1 | C3 raises the Swedish rate by at least 20 points over C0, and the 95% CI of (C3 - C5) excludes 0 | C5 gives a similar gain (any perturbation helps), or C3 gains less than 10 points |
| H2 | English rate on English prompts drops by at most 5 points; English perplexity rises by at most 5%; degeneration does not rise by more than 5 points | The edit is a global "always Swedish" switch, or it damages fluency |
| H3 | Math accuracy in Swedish changes by less than 5 points; Swedish perplexity does not fall | Swedish accuracy rises clearly (the edit adds something), or falls clearly (the switch costs quality) |
| H4 | C3 > C4 on the primary metric, and the selected config clearly beats a default config on dev | C4 matches C3 (the weights alone contain the needed information) |
| Practical value | C3 >= C1, or C6 > C1 | C1 (one sentence of prompt) matches or beats the edit with no regressions; then a weight edit is not worth it for this problem |

A result in the "challenged" column is a useful outcome, not a failure of the project. In particular, if prompting
solves the problem as well as the edit, the recommendation to SE.LLMA will say so.

## Deviations

Deviations 1 to 3 were made on 2026-11-19, **before any model was run** (no pilot or evaluation data had been
seen).

1. **Primary source of the activation direction.** The direction for C2/C3 is now computed from the model's *own*
   responses to Swedish prompts in a separate `contrast` prompt set: the mean activation over responses the model gave
   in English minus the mean over responses it gave in Swedish. Reason: this is closer to the paper's Qwen edit, which
   contrasted the model's own looping and productive contexts, and it targets the failure itself rather than
   language in general. Requirement: at least 20 responses in each language. If there are fewer, fall back to the
   original plan (paired Swedish/English translations, teacher-forced). The `contrast` set stays disjoint from dev
   and test.
2. **Pilot middle band.** If the lowest Swedish response rate among the candidates is between 75% and 90%, I still run
   the experiment on that model, and the report states that the headroom is small. (The original text covered only
   at most 75% and all above 90%.)
3. **Added stretch condition C8: LLM as search policy.** Claude chooses which layers, `k` and `alpha` to try, using
   the same dev evaluation budget as a random search over the same parameter grid. This tests the one part of the
   paper the scripted procedure leaves out: whether an LLM is a better search policy than chance. Run only if time
   allows; priority order for cutting: C7 first, then C8, then C6.

### Deviation 4: change of target after the pilot (written 2026-11-19, before any edit or test-set run)

**What happened.** Pilot 1 (40 `sv_open` dev prompts, greedy, `repetition_penalty=1.0`, 256 new tokens) failed the
precondition. Details in `docs/03_lab_notes.md`. In short:
- `lingua` labelled 100% (both Qwen models) and 85% (SmolLM2) of responses as Swedish, but hand checks found 0 to 1
  readable answers out of 10 per model. The primary metric counts prompt echoes and loops as "Swedish", so it is not
  valid for these models.
- No model shows "can write Swedish but chooses English". The Swedish ability itself is missing at this scale.
- The pre-registered fallback (Scandinavian leakage) cannot be measured, because the outputs are not coherent
  sentences.
- The pilot did show a strong instance of the paper's own failure: Qwen2.5-0.5B hit the token limit on 37/40 Swedish
  prompts and 39/40 responses contain a repeated 8-gram.

**New target.** Looping in Swedish generation, edited with the paper's own mechanism. This keeps the study close to
the paper's strongest result and lets it answer the assignment's question "new capability or removed failure?" in
Swedish.

**Risk of this change.** The target was chosen after seeing dev outputs. Mitigation: the choice is recorded here
before any direction is computed, before any weight is edited, and before any test-set prompt is run. The test sets are
unchanged and still unseen.

**Definitions.**
- *Loop:* a response in which some word-level 8-gram (whitespace tokens, lowercased) occurs at least 3 times.
  Secondary: response reaches `max_new_tokens`.
- *Early-stop check:* among non-looping responses, the median length must not fall below 50% of the C0 median. This
  guards against an edit that "fixes" loops by making the model stop almost at once.

**Pilot 2 (dev only, logged as feedback passes).**
- Models: `Qwen/Qwen2.5-0.5B-Instruct` (main), `Qwen/Qwen3-0.6B` (reference), same pinned revisions as pilot 1.
- Prompts: 40 `sv_open` dev, the 40 parallel `en_open` dev, 60 `sv_math` dev, 60 `en_math` dev.
- Decoding: (i) greedy, `repetition_penalty=1.0`; (ii) the model's recommended settings (Qwen2.5: T=0.7, top_p=0.8,
  top_k=20, `repetition_penalty=1.05`; Qwen3 non-thinking: its model-card values), fixed seed.
- `max_new_tokens`: 512 for open prompts, 512 for math.
- Gate: run the edit experiment on Qwen2.5-0.5B if its Swedish loop rate under greedy is at least 40%. Else use Qwen3-0.6B
  if it meets the same bar. If neither does, stop and report the pilots as the result.
- Predictions written now: (P1) the Swedish loop rate exceeds the English loop rate by at least 20 points; (P2)
  recommended settings reduce but do not remove Swedish loops.

**Conditions for the new target.** C0, C1, C2, C3, C5 and C6 keep their meaning, with `u` now a loop direction.
- `u` = mean activation over tokens inside a loop minus mean over tokens before the loop starts, from the model's own
  responses to the `contrast` prompts (token level, as in the paper's "matched productive/repetitive contexts"). The
  minimum of 20 examples in Deviation 1 applies to responses that contain a loop onset.
- **C4 is dropped.** Unlike response language, a loop has no natural direction that can be read from the embedding
  matrix without running the model. H4 is replaced by H4': how much does dev feedback matter? Compare C3 with a default
  configuration chosen before any dev pass (0 feedback passes), C3 with the dev-selected configuration (N passes,
  reported), and C5. This weakens the weights-versus-feedback comparison, and the report will say so.
- **C9 (new): decoding fix.** Unedited model with recommended settings. This is the inference-settings alternative the
  paper did not evaluate.
- Primary decoding for C0, C2, C3, C5: greedy with `repetition_penalty=1.0`. C9 and C3 are also both run with the
  recommended settings to see whether the edit adds anything on top of the decoding fix.

**Pre-registered thresholds for the new target (test set).**

| Hypothesis | Supported if | Challenged if |
|---|---|---|
| H1' (edit removes loops) | C3 lowers the Swedish loop rate by at least 20 points vs C0, and the 95% CI of (C3 - C5) excludes 0 | C5 does as well, or C3 lowers it by less than 10 points |
| H2' (no collateral damage) | English loop rate does not rise; `en_math` accuracy drops at most 5 points; perplexity on `sv_ref` and `en_ref` rises at most 5%; early-stop check passes | Any of these fails |
| H3' (failure removal vs capability) | "Unlocks hidden ability": `sv_math` accuracy rises at least 10 points and the gain sits mainly in items that looped under C0 (paper-style rescue strata). "Removes the failure only": loops fall at least 20 points but `sv_math` changes less than 5 points and coherence ratings do not rise | Neither pattern is clear |
| Practical value | C3 beats C9 on loop rate with no extra regressions, or C3 + recommended settings beats C9 alone | C9 matches or beats C3: a decoding change is enough |

**Coherence rating (secondary, for H3' on open prompts).** A fixed random sample of 40 `sv_open` test responses per
condition, shuffled and stripped of condition labels, rated 1 (incoherent), 2 (partly coherent), 3 (coherent and on
topic) by a frontier model with a fixed rubric. The rubric and all ratings are released. This is reported as a
secondary measure because the rater is an LLM.
