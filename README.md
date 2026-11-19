# Can a targeted weight edit fix language confusion in a small Swedish-capable model?

Candidate assignment for SE.LLMA: an investigation of
[Sparks of Weight-Space Programming](https://rikiyat.github.io/blog/weight-space-programming/) (Takehi et al., 2026)
applied to one Swedish-relevant question.

**Status:** work in progress. Analysis and pre-registered plan are done; experiments are next.

## Question in one paragraph

The paper's strongest language-model result (Qwen3.5-0.8B, MATH-500 7.9% to 48.1%) came from removing a failure
(thinking loops), not from adding ability. The Swedish failure with the same shape is *language confusion*: a model
that can write Swedish but answers Swedish prompts in English. I test whether a sparse rank-1 weight edit of the same
form fixes it, compare it against prompting, steering and random edits, check for regressions, and measure how much
of the edit's information comes from the weights alone versus from forward passes and feedback.

## Repository layout

```
docs/01_paper_analysis.md   critical analysis of the paper
docs/02_hypothesis.md       hypothesis, methods, metrics, pre-registered thresholds
data/                       synthetic Swedish/English prompt sets (dev/test/contrast splits)
src/                        directions, edits, evaluation
scripts/                    entry points to reproduce each step
results/                    raw generations, scores, frozen configs
report/                     research note (Markdown) and PDF report
AI_USAGE.md                 AI tools used and what they contributed
```

## Reproduce

To be added.
