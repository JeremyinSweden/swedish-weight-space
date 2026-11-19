# Coherence rating notes (Claude, blind)

Rater: Claude (Opus 5.5), in the main project chat. Rated all 160 items in `coherence_blind.jsonl` before seeing
`coherence_key.json`, `summary.md` or `examples.md`. Items were read in file order; long responses were read as the
first ~600 and last ~200 characters, plus the full text for borderline items.

How the rubric was applied (decided while rating batch 1, applied to all items):
- **1**: repetition dominates, or the text contains no correct or sensible point about the prompt (word salad,
  wrong topic, invented facts, refusal).
- **2**: on topic and partly understandable, with at least one sensible point toward the prompt, but clear errors or a
  long repetitive stretch. Two edge cases were also rated 2: (a) coherent answers written in English instead of
  Swedish (the rubric does not cover language; flagged here), and (b) understandable Swedish that misreads the prompt
  (desk "exercises" read as writing exercises).
- **3**: never given. No response was understandable Swedish that answered the prompt.

Result: 145 items rated 1, 15 rated 2, 0 rated 3.
