# 1. Critical analysis of "Sparks of Weight-Space Programming"

**Source.** Takehi, Teoh, Zhang, Khattab (MIT CSAIL), blog post, 2 November 2026. Released logs: <https://github.com/RikiyaT/lm_understand-logs> (read for this analysis; file paths below refer to that repo). Editor model in all experiments: GPT-6 Astra via the Codex CLI.

The post claims that frontier LLMs can "natively read and write" neural network weights. It reports eight experiments. The most important thing to notice is that they give the editor very different kinds of access, so they test different claims. I group them by where the information that drives the result comes from.

| Group | Experiments | What the editor had | What the result can show |
|---|---|---|---|
| A. Weights only, zero feedback | 1 (identify game), 2 (identify diffusion shape), 3 (identify training corpus), 4 (repair car policy), 5 (write MinAtar policies) | Weights (or rules/source code), no forward passes. Exp 3 allowed linear algebra in Python but no running of any layer | Reasoning *directly about weights* |
| B. Weights + model feedback | 7 with attention tool, 8 (Qwen math), 6 (Go) | Forward passes: generations, hidden states, MLP activations, attention patterns; a budget of 10 to 50 passes | Search guided by *repeated model feedback*, with an LLM as the search policy |

## 1.1 Strongest evidence

1. **Exp 8 shows a real, transferable, well-documented effect, and also shows what kind of effect it is.** The 50-pass edit to Qwen3.5-0.8B changes 131,072 weights (2 x 64 MLP output columns in layers 15 and 19) and moves MATH-500 from 7.9% to 48.1%. The benchmarks were never shown to the editor, the diff is released and rebuilds the evaluated checkpoint bit for bit with hash checks, and the per-problem outputs are public. This is the most reproducible result in the post. The most informative number is buried in the run's final log (`exp8_math/runs/p50c/state.json`, "RESCUE STRATA", 1,152 held-out practice problems):

   | Practice problems | n | Original acc. | Edited acc. |
   |---|---:|---:|---:|
   | Original answer finished within the token limit | 114 | 93.9% | 93.9% |
   | Original answer cut at the token limit (looping) | 1,038 | 1.4% | 56.7% |

   576 of the 579 rescued problems were ones where the original model never finished. On problems it already finished, the edit changed nothing. So the edit removes a generation failure (thinking loops that hit the 32,768-token limit; 93% of unedited MATH-500 answers were cut). It does not add mathematical skill.
2. **The Gemma 3 270M follow-up is an honest negative control, and the authors report it.** Gemma rarely loops (8.5% of answers hit the limit). With the same harness and up to 50 passes, MATH-500 moved from 6.8% to 7.0 to 7.7%, which is noise. Together with the rescue strata, this supports the authors' own reading: weight edits can remove an obstacle that hides an existing ability, but here they did not create a missing one.
3. **Exp 4 is the strongest zero-feedback result.** From the weights, the scene and one recorded failing trajectory, in one reply without tools, the editor produced a car policy that succeeds in 1,024 of 1,024 episodes (baseline failed all 256). The network is small (171,664 weights) and the failure is concrete, but no feedback loop could have found this edit.
4. **Exp 3 found induction heads without running the network.** For three 7M-weight character transformers, the heads labelled "copy" match the measured induction heads (score above 0.2) in all six conversations.

## 1.2 Most important limitations

1. **The headline result is in Group B, but it is framed as Group A.** The Qwen edit is described as "reading the raw weights", yet the logs show the direction was built from *activations*: "matched productive/repetitive contexts localized the relevant MLP writers", then "dose-response tests, layer-isolation tests, and a norm-matched random control" using up to 50 forward passes, each returning up to 512 generations or 1,024 teacher-forced reads with hidden states (`exp8_math/README.md`, `runs/p50c/final_answer.md`). The 50-pass run took 158 turns, 80 Python runs and 20 hours. This is closer to automated interpretability plus guided search than to reading weights.
2. **The edit form is a known technique.** Subtracting a direction from selected output columns is directional ablation / activation steering written into the weights (compare the refusal-direction work of Arditi et al., 2024, which the post cites). An independent, unreviewed analysis (braindetox.kr) reports that the edit is effectively rank 1, close to a constant push along one direction, and that a plain steering vector at 1x strength recovers almost all of the gain (MATH-500 50.8 vs 53.2), with loops returning at 0.5x and reasoning degrading at 2x. If this holds, the LLM's contribution is *finding* the direction and layers, not a new kind of edit.
3. **No external baselines on the benchmarks.** The reported comparison is only against the unedited model. There is no benchmark-level comparison to: thinking mode off, a different repetition penalty or a lower token limit, a steering vector, a short LoRA fine-tune, or a random edit. The model card itself says this model is prone to thinking loops and recommends inference-side mitigations. With 93% of baseline answers truncated, a cheap inference change could plausibly recover much of the gain; we cannot tell from the post.
4. **One run per budget, not monotone, different mechanisms.** The 10, 25 and 50-pass runs found different edits (rank-1 projection on 30 matrices; zeroing one attention head; 128 MLP columns) with gains of +4, +6 and +40 points on MATH-500. With n = 1 per budget, we cannot separate the effect of budget from run-to-run variance, and we do not know how often the procedure fails.
5. **Group A results are on tiny networks with small answer sets and some lenient grading.** The networks have 17k to 7M weights. Identification tasks have 3 or 4 options (chance 25 to 33%), and the two conversations per network in Exp 3 are not independent samples. Stated probabilities in Exp 3 were modest (0.48 to 0.62). "Frogger" was accepted for a Freeway-like game (Exp 1), and the shapes in Exp 2 were described as outlines while the networks drew filled shapes. The three corpora in Exp 3 (Python, romaji, English) are very different; distinguishing closely related languages (for example Swedish vs Norwegian) would be a much harder test.
6. **Weights alone failed on the one LLM behaviour task.** In Exp 7 (which of two Gemma fine-tunes is sycophantic), four weights-only attempts failed; with a tool exposing attention patterns (a form of forward pass) it succeeded 3/3. For billion-parameter language models, the evidence for pure weight reading is negative so far.
7. **Exp 5 compiles given rules.** The editor received the exact game source and rules. Writing a good Breakout policy by hand-designing weights is impressive, but comparing it to PPO measures something different from learning.

## 1.3 Which conclusions are and are not justified

**Justified.**
- A frontier LLM agent with Python access and a modest forward-pass budget can diagnose a dominant, visible failure mode in a sub-1B language model and write a sparse weight patch (0.016% of weights) that removes it, and the patch transfers to held-out benchmarks.
- When the failure is removed, latent ability shows up (math, IFEval, MMLU-Pro and GPQA all rise). When there is no failure to remove (Gemma), nothing improves.
- On small networks, frontier LLMs can extract non-trivial structure (induction heads, game identity, a policy bug) from weights without running them.

**Not justified (yet).**
- That the edit made Qwen "better at math" in the sense of a new capability. The rescue strata say it did not.
- That the headline result comes from *natively reading raw weights*. It comes from activation analysis and search with model feedback.
- That weight-space programming beats or matches conventional methods. No baselines were run.
- That the method is reliable. There is one run per setting and no failure rate.
- That weights-only reasoning scales to LLMs. The only LLM test of it (Exp 7) failed.

## 1.4 What this means for SE.LLMA

For building strong Swedish models, most weaknesses of a small model are capability gaps (vocabulary, grammar, knowledge about Sweden). The Gemma result predicts that targeted edits will not fix those. The paper's evidence is relevant only where a model *has* the ability but a systematic failure stops it from using it. The most common failure of that type for Swedish is **language confusion**: a multilingual model answers a Swedish prompt in English (or drifts into Norwegian or Danish). This is the case where the paper's mechanism could plausibly transfer, so it is the case I test. The question that matters for SE.LLMA is not only "does it work?" but "does it work better than the cheap alternatives (a system prompt, a steering vector), and does the information come from the weights or from feedback?"
