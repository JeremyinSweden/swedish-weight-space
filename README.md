# Can a sparse weight edit remove looping in Swedish generation?

Candidate assignment for SE.LLMA, based on [Sparks of Weight-Space Programming](https://rikiyat.github.io/blog/weight-space-programming/) (Takehi et al., 2026).

- Research note (about 2 pages): [`report/research_note.md`](report/research_note.md)
- Full report with all tables and examples: [`report/report.pdf`](report/report.pdf) (source: `report/report_long.md`)
- AI usage: [`AI_USAGE.md`](AI_USAGE.md)

## Question

The paper's strongest language-model result is a sparse weight edit that raised a small Qwen model's MATH-500 score from 7.9% to 48.1%. The authors' own logs show that the gain came from removing thinking loops, not from new math skill, and that the edit direction was found with forward passes, not by reading weights alone.

I tested whether the same edit form helps a small model in Swedish. A first pilot showed that the planned target (answering Swedish prompts in English) does not exist at this scale. A second pilot showed the paper's own failure in Swedish: `Qwen/Qwen2.5-0.5B-Instruct` loops on 90% of Swedish open prompts under greedy decoding, against 22% in English. The main experiment asks whether the paper's edit form removes that looping without regressions, whether it beats a random edit, a steering vector and the model's default decoding settings, and whether removing the loops reveals hidden Swedish ability.

The weight edit is computed by a script and selected by a rule fixed in advance. No LLM reads the weights or chooses the edit. This tests the paper's edit form, not its claim that an LLM can find edits (see `AI_USAGE.md`).

## Main result

Under the decoding setting where looping is strongest (greedy, no repetition penalty), the paper-style weight edit has no effect; the model's shipped decoding settings remove most of the looping on their own, and removing the looping does not make the Swedish answers coherent.

| Condition (120 Swedish test prompts) | Loop rate | Change vs unedited (95% CI) |
|---|---:|---|
| C0 unedited, greedy | 90% | |
| C3 weight edit (paper form), greedy | 94% | +4.2 points (-2.2 to +10.5) |
| C5 random edit, 3 seeds | 90 / 93 / 91% | +1.4 points (mean) |
| C1 Swedish system prompt | 79% | -10.8 points (-22.0 to 0.0) |
| C2 steering vector | 56% | -34.2 points, but 14% of answers cut under 30 tokens |
| C9 shipped decoding defaults | 22% | -68.3 points (-76.3 to -60.5) |
| C3 + shipped defaults | 24% | +2.5 points vs C9 (-8.5 to +12.9) |

With the loops removed by decoding, 0 of 28 rescued answers were rated coherent, and Swedish math accuracy stayed at 22-30% (English 73%). This repeats the paper's Gemma result in Swedish: the ability is missing, so there is nothing for an edit to release. Recommendation: not a priority for SE.LLMA; check ability and inference settings first.

## Repository layout

```
scripts/      Experiment code, numbered by step
  00_env_check.py    check Python packages and MPS
  01_make_data.py    build the synthetic data sets (deterministic, seed 20261119)
  02_pilot.py        pilot 1: language-confusion precondition (3 models)
  03_pilot2.py       pilot 2: loop precondition and decoding check
  04_direction.py    step 4: loop direction from the model's own answers
  05_dev_select.py   step 5: dev selection, writes configs/frozen.json and the edit diffs
  06_test.py         step 6: test run, summary tables, coherence sample, examples
  07_coherence_summary.py   coherence means, CIs, rescue strata and rater agreement from the blind ratings
  common.py, runner.py, edits.py, metrics.py, data_sources.py   shared code and prompt sources
configs/      models.json, pilot2.json, step4_6.json (spec fixed before any dev pass),
              frozen.json (test config, committed before the test run)
data/         Synthetic prompt sets (dev/test/contrast splits), MANIFEST.json with SHA-256 hashes, SPOTCHECK.md
results/      All outputs
  pilot/, pilot2/      pilot answers and summaries
  direction/           u.npz (loop direction) and summary.json
  dev/                 dev answers for every configuration, summary.md
  edits/               edit diffs (column indices and values, never full checkpoints)
  test/                per-condition answers (<condition>__<set>.jsonl), summary.md, summary.json,
                       examples.md, coherence rubric, blind sample, key, ratings and agreement
  feedback_log.jsonl   every model pass used for selection, with its purpose
  model_revisions.json, env.json
docs/         01_paper_analysis.md, 02_hypothesis.md (pre-registration, Deviations 1-5),
              03_lab_notes.md, 04_results_interpretation.md
report/       research_note.md, report_long.md, report.pdf
AI_USAGE.md   AI tools used and what they did
```

## Model versions and seeds

| Item | Value | Recorded in |
|---|---|---|
| Model | `Qwen/Qwen2.5-0.5B-Instruct`, revision `7ae557604adf67be50417f59c2c2f167def9a775` (Apache 2.0) | `results/model_revisions.json`, `configs/frozen.json` |
| Pilot-only models | `Qwen/Qwen3-0.6B` `c1899de2`, `HuggingFaceTB/SmolLM2-360M-Instruct` `a10cc151` | `results/model_revisions.json` |
| Global seed | 20261119 (data, sampled decoding, coherence sample, examples) | `configs/step4_6.json`, `configs/frozen.json`, `data/MANIFEST.json` |
| Random-edit seeds (C5) | 0, 1, 2 | `configs/frozen.json` |
| Greedy decoding | `do_sample=False`, `repetition_penalty=1.0`, 512 new tokens, batch size 40 | `configs/step4_6.json` |
| Shipped defaults (C9) | T 0.7, top_p 0.8, top_k 20, `repetition_penalty=1.1`, from the [model's generation_config.json](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/blob/7ae557604adf67be50417f59c2c2f167def9a775/generation_config.json) | `configs/frozen.json`, `results/pilot2/repo_generation_defaults.json` |
| Environment | Python 3.14.5, torch 2.15.0, transformers 4.57.6, Apple M1 Pro MacBook Pro (MPS, float32) | `results/env.json` |

## Reproduce

Setup (about 1 GB model download on first run):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/00_env_check.py
```

**Quick check** (about 2 minutes after setup, plus the model download on first run). Rebuilds the data, then regenerates one test cell (the frozen edit C3 on the 100 Swedish math prompts) and compares it with the committed file:

```bash
python scripts/01_make_data.py && git status --porcelain data/
mv results/test/C3__sv_math.jsonl /tmp/ && python scripts/06_test.py --deadline 23:59
git status --porcelain results/test/
```

Expected: the first `git status` prints nothing (the data is identical). Before generating, the runner checks that the recomputed edit matches `results/edits/C3_selected.npz`; the run then prints `sv_math loops 2/100 acc 28/100` and skips every other cell. The last `git status` lists only `coherence_author20.md` (overwritten with a blank sheet; restore it with `git checkout -- results/test/coherence_author20.md`), `run_status.json` and `summary.json` (timestamps). `C3__sv_math.jsonl` and `summary.md` are not listed: on the author's Apple M1 Pro MacBook Pro the regenerated answers were identical to the committed ones (checked from a fresh clone on 2026-11-19). Other hardware or library versions may differ slightly.

**Main experiment, one command** (re-runs the full test set with the frozen config; about 60 minutes on an Apple M1 Pro MacBook Pro):

```bash
mv results/test results/test_original && python scripts/06_test.py --deadline 23:59
```

The original outputs are kept in `results/test_original/`. Compare with `diff results/test/summary.md results/test_original/summary.md`. Before generating, the script recomputes the C3 edit from the model and `results/direction/u.npz` and checks it against the frozen diff in `results/edits/`. `--deadline` is a local stop time for today (HH:MM): the runner does not start a new cell after it, so set it at least 75 minutes ahead. Greedy outputs should match closely; sampled conditions (C9, C3 + defaults) can differ on other hardware.

**Recompute the tables only** (seconds, no generation):

```bash
python scripts/06_test.py --summary-only && git checkout -- results/test/coherence_author20.md
```

The `git checkout` restores the author's blind ratings, which the summary step overwrites with a blank rating sheet.

Recompute the coherence summary (`results/test/coherence_summary.json`) from the blind ratings (`coherence_ratings_claude.txt`, `coherence_key.json`, `coherence_author20.md`); no model needed:

```bash
python scripts/07_coherence_summary.py
```

**Full pipeline from scratch** (about 1.5 hours). Steps 4 and 5 overwrite the direction, dev results, edit diffs and `configs/frozen.json`, and step 5 skips dev cells that already exist, so move the old outputs aside first:

```bash
mkdir -p results/original && mv results/direction results/dev results/edits results/test results/original/
python scripts/01_make_data.py        # rebuilds data/; afterwards `git status data/` shows no changes
python scripts/02_pilot.py            # pilot 1, optional (3 models)
python scripts/03_pilot2.py           # pilot 2, optional (2 models)
python scripts/04_direction.py        # about 5 minutes
python scripts/05_dev_select.py       # about 15-20 minutes
git add configs/frozen.json && git commit -m "Freeze config before test run"
python scripts/06_test.py --deadline 23:59   # about 60 minutes; refuses to run if frozen.json is not committed
```

Scripts 02 to 06 also take `--mock` to test the pipeline without downloading a model (run 04, 05 and 06 in that order; mock outputs go to `results/*_mock/` and `configs/frozen_mock.json`, which git ignores).

## Data and licences

All prompts and reference paragraphs were written with Claude for this project (`scripts/data_sources.py`) and spot-checked by the author. They contain no third-party text. The model is released under Apache 2.0.
