---
title: "Can a weight edit stop a small model from looping in Swedish?"
subtitle: "A small test of Sparks of Weight-Space Programming for SE.LLMA"
---

Short version: `report/research_note.md`. Pre-registered plan and all deviations: `docs/02_hypothesis.md`. Raw outputs: `results/`.

## The short answer

No. The paper-style weight edit did nothing. The model's own default decoding settings removed most of the looping. And once the loops were gone, the Swedish answers were still not coherent, because the model cannot write good Swedish in the first place.

## Why I tested this

The paper's best result is a weight edit that raised a small Qwen model's math score from 7.9% to 48.1%. The authors' logs show the edit stopped the model from looping; on problems it already finished, accuracy did not change. So it removed a failure rather than adding skill. The edit was found by running the model up to 50 times, not by reading weights alone, and it was never compared with simple alternatives such as other decoding settings.

My first idea was a model that answers Swedish prompts in English. A pilot showed this does not happen at this size: the models cannot write readable Swedish at all. But it showed the paper's own problem in Swedish. Qwen2.5-0.5B-Instruct loops on 90% of Swedish prompts and 22% of the same prompts in English. So I changed the target to looping, and wrote that down before running any edit or test.

## Hypothesis

If looping hides real Swedish ability, a targeted edit should remove the loops, and the answers should then get better. I fixed the thresholds in advance (`docs/02_hypothesis.md`):

- **Supported:** the edit cuts Swedish loops by at least 20 points, does better than a random edit, and breaks nothing else.
- **Challenged:** a random edit does just as well, the edit cuts loops by less than 10 points, or a simple decoding change does as well as the edit.
- **New ability or just a removed failure?** If the loops go away and the answers become coherent, ability was hidden. If the loops go away and the answers stay bad, only the failure was removed.

## Experiment

- **Model:** Qwen2.5-0.5B-Instruct, pinned revision `7ae55760`, on an Apple M1 Pro MacBook Pro.
- **Data:** synthetic prompts; test set of 120 Swedish and 120 English questions and 100 math problems per language. The edit was built and tuned on separate prompts.
- **The edit:** the same form as in the paper. A script finds the direction the model moves in when it starts to loop, then removes that direction from some output weights in two layers. No LLM looked at the weights or chose the edit.
- **Comparisons:** unedited model, random edit of the same size, Swedish system prompt, steering vector (same direction, removed at run time), default decoding settings. Damage checks: English loops, English math, perplexity, answer length.
- **Quality:** Claude rated 40 Swedish answers per condition from 1 (incoherent) to 3 (coherent), blind to the condition. I rated 20 blind and agreed on 17.

## Results (test set)

| Method | Swedish answers that loop | Change vs unedited (95% CI) |
|---|---:|---|
| Unedited model | 90% | |
| Weight edit (paper's form) | 94% | +4 points (-2 to +11) |
| Random edit, same size | 90-93% | about +1 point |
| Swedish system prompt | 79% | -11 points (-22 to 0) |
| Steering vector | 56% | -34 points, but 14% of answers were cut very short |
| Default decoding settings | 22% | -68 points (-76 to -61) |
| Weight edit + default decoding | 24% | +2 points vs default decoding alone |

The edit broke nothing, but it also changed nothing. On the dev set, none of the seven edit versions I tried reduced loops either, including the exact setup from the paper.

With default decoding, 28 of 37 looping answers in the rated sample stopped looping. None of them was rated coherent. No answer in any condition got the top score. Swedish math stayed between 22% and 30% in every condition except steering, where it fell to 16% (English: 73%).

## What this means

- **The edit does not work here.** It is no better than a random change of the same size.
- **A free fix beats it.** The model's default decoding settings remove most of the loops. The paper did not test this kind of baseline.
- **Removing the failure does not reveal hidden ability.** My pre-registered test of this was for the edit, and since the edit removed nothing, that test is unclear. Looking at the decoding fix instead (not pre-registered): loops fell by 68 points, but quality barely moved and Swedish math went from 26% to 22% (not a paired test). This matches the paper's own Gemma result: when the ability is missing, there is nothing to unlock.

Why the edit failed is open. Steering did cut loops, but the direction may partly measure "late in the answer" rather than "looping", and steering's short answers fit that reading.

## Recommendation

SE.LLMA should not spend effort on this kind of weight edit to improve Swedish in small models. Before trying any weight-level fix, run two cheap checks: can the model do the task when the failure is absent, and are the default inference settings in use? Both took minutes here.

**Next experiments, if there were more time:**

1. Repeat on Qwen3-0.6B, which writes better Swedish (67% on Swedish math) and whose loops do not go away with decoding settings. That is the case where an edit could actually help.
2. Build the direction by comparing looping and non-looping text at the same position in the answer.
3. Let a frontier LLM choose the edit, which is the paper's real claim and was not tested here.

## Appendix A. Full test results

| Method | Swedish loops | Answers under 30 tokens | Swedish math | English loops | English math |
|---|---:|---:|---:|---:|---:|
| Unedited model (greedy) | 90% | 1% | 26% | 14% | 73% |
| Weight edit | 94% | 0% | 28% | 14% | 73% |
| Random edit, seeds 0 / 1 / 2 | 90 / 93 / 91% | 1-2% | 24 / 24 / 29% | | |
| Swedish system prompt | 79% | 2% | 30% | | |
| Steering vector | 56% | 14% | 16% | | |
| Default decoding | 22% | 0% | 22% | 0% | 73% |
| Weight edit + default decoding | 24% | 1% | 26% | 0% | 69% |

Weight edit vs random edit (mean of 3 seeds): +2.8 points (95% CI -2.3 to +7.2). Perplexity on Swedish and English reference text did not change (Swedish 91.0 vs 90.9). CIs are paired cluster bootstraps over topics; exact McNemar p-values are in `results/test/summary.md`.

**Quality ratings** (40 fixed Swedish prompts, 1 = incoherent, 3 = coherent, blind):

| Method | Mean | Rated 2 | Rated 3 |
|---|---:|---:|---:|
| Unedited | 1.05 | 2 | 0 |
| Weight edit | 1.05 | 2 | 0 |
| Default decoding | 1.18 | 7 | 0 |
| Weight edit + default decoding | 1.10 | 4 | 0 |

My blind ratings of 20 items agreed with Claude's on 17; the three disagreements were all between 1 and 2.

**Dev selection.** The paper's own setup (layers 15 and 19, 64 columns) was the starting point; six more versions were fixed in `configs/step4_6.json` before any dev run. All seven gave 92-95% Swedish loops against 90% for the unedited model. A rule fixed in advance picked 1,024 columns per layer (1.8M weights, 0.4% of the model). Every dev run is logged in `results/feedback_log.jsonl`.

## Appendix B. Two examples

Prompts from the fixed-seed sample in `results/test/examples.md` (all five are there). Text cut at about 250 characters.

**"Skriv ett kort stycke om varför is flyter på vatten."** (Why does ice float on water?)

- Unedited (loops): "Is flyter på vatten för att följa en specifik försatsystem eller för att följa en specifik försatsystem. Detta kan vara en specifik försatsystem..." The weight edit gave the same text.
- Default decoding (no loop): "Is flytning på vatten är en viktig teknik i skärning och hälsa..." No loop, but it calls floating ice "a technique in cutting and health".
- Steering (17 tokens): "Is flyter på vatten för att föra vatten till vatten." ("Ice floats on water to carry water to water.") The loop stops because the answer stops.

**"Kan du förklara vad en algoritm är för en tolvåring?"** (Explain an algorithm to a twelve-year-old.)

- Unedited and weight edit (both loop): "En algoritm är en struktur för att utveckla en funktion eller en funktion som kan användas för att utveckla en algoritmer..."
- Default decoding (no loop): "Ett algoritmus är ett sätt att解决问题 eller skapa en funktion som ger en räknbar rekor..." No loop, but vague, and it switches into Chinese mid-sentence.

## Limitations

- One small model, one direction estimate, one sampling seed for the decoding runs.
- Quality ratings sit near the floor (145 of 160 rated 1), and the main rater is an AI.
- Default decoding changes several settings at once; which one removes the loops was not tested.
- The loop detector misses repetition inside a single word.
- Prompts are synthetic. The target changed after the first pilot, before any edit or test run.

## Reproducibility

Model revision, seeds and environment: `results/model_revisions.json`, `configs/frozen.json`, `results/env.json`. Commands to reproduce: `README.md`. The edit is never stored as a full checkpoint; its diff is in `results/edits/`.

## References

- Takehi, Teoh, Zhang, Khattab. "Sparks of Weight-Space Programming." MIT CSAIL, 2 November 2026. Logs: <https://github.com/RikiyaT/lm_understand-logs>.
- Arditi et al. "Refusal in Language Models Is Mediated by a Single Direction." NeurIPS 2024. arXiv:2406.11717.
- Qwen2.5-0.5B-Instruct `generation_config.json`: <https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/blob/7ae557604adf67be50417f59c2c2f167def9a775/generation_config.json>.
