# Can a weight edit stop a small model from looping in Swedish?

Full report with all tables and examples: `report/report.pdf`.

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

**Limitations:** one small model, one direction, one sampling seed; quality ratings near the floor, mainly by an AI; synthetic prompts. **References:** Takehi et al., "Sparks of Weight-Space Programming", MIT CSAIL, 2026 (logs: <https://github.com/RikiyaT/lm_understand-logs>); Arditi et al., "Refusal in Language Models Is Mediated by a Single Direction", NeurIPS 2024.
