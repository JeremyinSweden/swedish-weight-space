# 4. Test results and interpretation (checkpoint b)

Written 2026-11-19, after the test run (`results/test/summary.md`) and after the blind coherence ratings
(`results/test/coherence_ratings_claude.txt`, rated before the key was opened; summary in
`results/test/coherence_summary.json`). Thresholds are the ones fixed in Deviations 4 and 5.

## 4.1 What was tested

Model: `Qwen/Qwen2.5-0.5B-Instruct` (revision `7ae55760`). Failure: looping in Swedish open-ended answers (90% of
120 Swedish test prompts under greedy decoding, 14% of the parallel English prompts).
Frozen edit (C3): the paper's edit form, `W' = W - alpha * u (u^T W)`, on the MLP `down_proj` columns of layers 15 and 19,
k = 1024 columns per layer, alpha = 1.0. The direction `u` is the mean residual activation inside loops minus before the
loop starts, from the model's own answers to 150 separate Swedish prompts (133 usable looping answers).
On dev, none of the 7 candidate configurations (including the zero-feedback copy of the paper's placement, k = 64)
reduced loops: 92-95% vs 90% for the unedited model. C3 was then chosen by the pre-registered selection rule
(details in `results/dev/` and `configs/frozen.json`). For steering (C2), neither candidate strength met all dev
constraints (alpha_s = 1.0 had 25% English loops vs 22% for C0, one response), so alpha_s = 1.0 was chosen by the
fallback rule; `frozen.json` does not flag this.

## 4.2 Results (test set, Swedish open prompts unless stated)

| Condition | Loop rate | Change vs C0 (95% CI) | Side effects |
|---|---:|---|---|
| C0 unedited, greedy | 90% | - | - |
| C3 weight edit (paper form), greedy | 94% | +4.2 pts (-2.2 to +10.5) | none: English loops, en_math, perplexity unchanged |
| C5 random edit, 3 seeds (same columns, same norm) | 90 / 93 / 91% | +1.4 pts (mean) | none |
| C1 Swedish system prompt | 79% | -10.8 pts (-22.0 to 0.0) | none detected |
| C2 steering (project out `u` at inference) | 56% | -34.2 pts (-46.1 to -22.2) | 14% of answers under 30 tokens (fails early-stop check); sv_math 26% to 16% |
| C9 shipped decoding defaults (T 0.7, top_p 0.8, top_k 20, rep. penalty 1.1) | 22% | -68.3 pts (-76.3 to -60.5) | none detected |
| C3 + shipped defaults | 24% | vs C9: +2.5 pts (-8.5 to +12.9) | none detected |

Swedish math accuracy stays between 22% and 30% in every condition except steering (16%); English math is 69-73%.
Swedish perplexity: 91.0 (C0) vs 90.9 (C3).

Coherence (40 fixed Swedish test prompts, 1-3 scale, blind):

| Condition | Mean | Rated 2 | Rated 3 | Of the 37 prompts that looped under C0: now not looping / rated 3 |
|---|---:|---:|---:|---|
| C0 | 1.05 | 2 | 0 | - |
| C3 | 1.05 | 2 | 0 | 1 / 0 |
| C9 | 1.18 | 7 | 0 | 28 / 0 |
| C3 + defaults | 1.10 | 4 | 0 | 26 / 0 |

Paired differences: C9 - C0 = +0.13 (0.00 to +0.25); C3 - C0 = 0.00.
No response in any condition was rated 3 (coherent Swedish that answers the prompt).

Rater check: the author rated a random 20 of the 160 items blind (`results/test/coherence_author20.md`). Agreement
with Claude's ratings: 17 of 20 (85%). The 3 disagreements are all between 1 and 2 (R084, R089, R095), and neither rater
gave any item a 3. Cohen's kappa is -0.07, which is expected when almost every item falls in one category (the
prevalence effect), so percent agreement is the more useful number here. The main coherence finding, that no
condition produced coherent Swedish answers, holds for both raters.

## 4.3 Verdicts against the pre-registered thresholds

- **H1' (the edit removes loops): challenged.** C3 does not lower the loop rate (+4.2 points, CI includes 0) and is
  indistinguishable from random edits of the same size. The same holds on dev for all 7 configurations, including the
  paper's own placement.
- **H2' (no collateral damage): supported, but uninformative,** because the edit had no measurable effect at all.
- **H3' (failure removal vs new capability): answered through C9, not C3.** The pre-registered pattern "removes the
  failure only" holds for the decoding fix: loops fall by 68 points, mean coherence rises by only 0.13 (threshold for
  "unlocks ability": 0.5), 0 of 28 rescued answers are coherent, and Swedish math does not move. Removing the loops
  did not reveal hidden Swedish ability. This is the paper's Gemma result, reproduced in Swedish with a different way
  of removing the failure.
- **Practical value: challenged.** The shipped decoding defaults alone cut Swedish loops from 90% to 22%. The edit
  adds nothing on top of them (+2.5 points, CI -8.5 to +12.9).

**Summary sentence for the report:** under the decoding setting where looping is strongest (greedy, no repetition
penalty), the paper-style weight edit has no effect; the model's shipped decoding settings remove most of the looping
on their own, and removing the looping does not make the Swedish answers coherent.
- **H4' (does dev feedback matter?): no signal.** Neither the zero-feedback configuration nor any feedback-selected
  configuration worked, so feedback could not be shown to help. Every dev pass is logged in `results/feedback_log.jsonl`.

## 4.4 Interpretation

1. **The paper's edit form did not transfer to this model and failure.** A mean-difference direction written out of
   up to 2 x 1024 MLP columns changed nothing, while removing the same direction from the whole residual stream
   (steering) did reduce loops. Two explanations fit and were not separated here: (a) loops in this model are driven
   mainly by components other than the selected MLP columns (attention, other layers), so a column-restricted edit is too
   weak; (b) the direction is partly a confound. "In-loop" tokens always come later in the answer than "pre-loop"
   tokens, so `u` may encode position or answer length as much as looping. Steering's side effects (very short answers,
   lower math accuracy) are consistent with (b): it cuts loops partly by cutting answers.
2. **The binding constraint is Swedish ability, not looping.** Three independent observations agree: pilot 1 (no
   readable Swedish), pilot 2 and test (Swedish math 22-30% vs English 69-73%, on answers that do not loop), and the
   coherence ratings (loop removal by decoding gives 0 coherent answers).
3. **Cheap checks found the important facts.** The shipped decoding defaults were the strongest method tested. The
   90% loop rate was measured under greedy decoding without a repetition penalty; with the settings the model ships
   with, it is 22%. The paper did not report this kind of baseline for its Qwen result.

## 4.5 Limitations

- One model (0.5B), one failure, one direction estimate, one frozen configuration; greedy decoding for most conditions,
  one sampling seed for C9 and C3 + defaults.
- Coherence ratings are near the floor (145 of 160 items rated 1), so the measure has little resolution. The main
  rater is an LLM (Claude); the author's 20-item blind check agrees on 85% of items.
- C9 changes several decoding settings at once (sampling with T 0.7, top_p 0.8, top_k 20, plus repetition penalty 1.1).
  Which of them removes the loops was not tested.
- Synthetic prompts; math uses 15 templates shared between dev and test with different numbers.
- The edit was computed by a fixed script, not by an LLM reading weights. This tests the paper's edit form, not its
  claim that an LLM can find edits by reasoning about weights (C8 was cut for time).
- The target changed after pilot 1 (Deviation 4) and the C9 setting was corrected after pilot 2 (Deviation 5). Both
  changes were committed before any edit or test run.

## 4.6 Recommendation (draft for the report)

On this evidence, weight-space edits of this kind are not a priority for improving the Swedish of small models. In
this study the weakness was missing ability, and removing the visible failure did not expose any hidden ability. Before any weight-level
intervention, check (1) that the model can do the task when the failure is absent and (2) that the shipped inference
settings are in use.

Most informative next experiments:
1. **Qwen3-0.6B** (recorded in Deviation 5 before the test): it has more Swedish ability (67% Swedish math on dev) and
   its loops did not respond to recommended decoding, which is exactly the case where an edit could add value.
2. **A position-matched direction**: compare in-loop tokens with non-looping tokens at the same position, to remove the
   confound in 4.4 (1b).
3. **LLM as search policy (C8)**: give a frontier model the same dev budget to choose layers, columns and strength,
   against random search, to test the paper's actual claim.
