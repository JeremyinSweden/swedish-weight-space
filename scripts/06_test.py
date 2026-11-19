"""Step 6: test evaluation (Deviation 5, item 7). Runs only after configs/frozen.json is committed.

Usage:  python scripts/06_test.py                 (about 45-75 min; resumable; stops at the 21:45 deadline)
        python scripts/06_test.py --summary-only  (recompute tables from saved cells)
        python scripts/06_test.py --mock

Conditions run in the priority order of configs/step4_6.json. Each (condition, set) cell is saved as soon as it
finishes; a re-run skips finished cells. Before starting a new cell after the deadline, the runner stops and
summarizes what finished.

Outputs (results/test/): <cond>__<set>.jsonl, <cond>__ppl.json, summary.json, summary.md, examples.md,
coherence_blind.jsonl, coherence_key.json (do not show to the rater), coherence_rubric.md, coherence_author20.md.
"""
import argparse
import datetime as dt
import json
import math
import random
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import edits as E  # noqa: E402
import metrics as M  # noqa: E402
import runner as R  # noqa: E402

SETS_FILES = {"sv_open": "sv_open_test.jsonl", "en_open": "en_open_test.jsonl",
              "sv_math": "sv_math_test.jsonl", "en_math": "en_math_test.jsonl"}
RUBRIC = """# Coherence rubric (fixed before rating; Deviation 5, item 2)

Rate each Swedish response to its prompt. Judge only the response text; ignore length beyond what the rubric says.

- **1 = incoherent**: mostly repetition, word salad, or not about the prompt; a reader learns nothing useful.
- **2 = partly coherent, on topic**: about the prompt and partly understandable, but with clear errors, broken
  sentences, wrong facts that undermine the answer, or a long repetitive stretch.
- **3 = coherent and on topic**: understandable Swedish that answers the prompt; minor grammar errors are fine;
  no long repetitive stretch.

Output one line per item: `<blind_id> <rating>`.
"""


def git_frozen_ok():
    try:
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "configs/frozen.json"], cwd=C.ROOT,
                                 capture_output=True).returncode == 0
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", "configs/frozen.json"], cwd=C.ROOT).returncode == 0
        return tracked and clean
    except FileNotFoundError:
        return False


def mcnemar_exact(a, b):
    """Two-sided exact McNemar on paired 0/1 lists."""
    n01 = sum(1 for x, y in zip(a, b) if x and not y)
    n10 = sum(1 for x, y in zip(a, b) if y and not x)
    n = n01 + n10
    if n == 0:
        return dict(b=n01, c=n10, p=1.0)
    k = min(n01, n10)
    p = min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)
    return dict(b=n01, c=n10, p=p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--summary-only", action="store_true")
    ap.add_argument("--deadline", default=None, help="HH:MM local; default from configs/step4_6.json")
    args = ap.parse_args()
    sfx = "_mock" if args.mock else ""
    frozen_path = C.CONFIGS / f"frozen{sfx}.json"
    if not frozen_path.exists():
        sys.exit("configs/frozen.json missing: run scripts/05_dev_select.py first")
    if not args.mock and not args.summary_only and not git_frozen_ok():
        sys.exit('STOP: configs/frozen.json is not committed (or has uncommitted changes).\n'
                 '  git add -A && git commit -m "Freeze config before test run"')
    F = json.loads(frozen_path.read_text(encoding="utf-8"))
    plan_spec = R.SPEC["test"]
    out_dir = C.RESULTS / f"test{sfx}"
    out_dir.mkdir(parents=True, exist_ok=True)
    data = {s: C.load_jsonl(C.DATA / f) for s, f in SETS_FILES.items()}
    ref = {l: C.load_jsonl(C.DATA / f"{l}_ref_test.jsonl") for l in ("sv", "en")}
    seed = F["seed"]

    if not args.summary_only:
        dl = args.deadline or plan_spec["deadline_local"]
        hh, mm = map(int, dl.split(":"))
        deadline = dt.datetime.now().replace(hour=hh, minute=mm, second=0, microsecond=0)
        ctx = R.Ctx(mock=args.mock).load()
        U = np.load(C.ROOT / F["direction_file"])["U"].astype(np.float64)
        layers = F["C3"]["layers"]
        if args.mock:
            rng = np.random.default_rng(1)
            W = {l: rng.standard_normal((896, 4864)) * 0.02 for l in layers}
        else:
            W = E.read_weights(ctx.model, layers)
        plans = {"selected": E.edit_plan(W, U, layers, F["C3"]["k"], F["C3"]["alpha"])[0]}
        for s in (0, 1, 2):
            plans[f"random{s}"] = E.edit_plan(W, U, layers, F["C3"]["k"], F["C3"]["alpha"], random_seed=s)[0]
        saved = np.load(C.ROOT / F["C3"]["diff_file"])
        for l in layers:  # the recomputed edit must match the frozen diff (mock weights are random, so skip there)
            if not args.mock:
                assert np.array_equal(saved[f"L{l}_idx"], plans["selected"][l][0]), "edit differs from frozen diff"
                assert np.allclose(saved[f"L{l}_delta"], plans["selected"][l][1], atol=1e-5), "delta differs"
        strength = {"base": 0.0, "selected": 0.6, "random0": 0.05, "random1": 0.05, "random2": 0.05}
        stopped = None
        for cond in plan_spec["conditions"]:
            cid = cond["id"]
            todo = [s for s in cond["sets"] if not (out_dir / f"{cid}__{s}.jsonl").exists()]
            need_ppl = cond.get("ppl") and not (out_dir / f"{cid}__ppl.json").exists()
            if not todo and not need_ppl:
                print(f"{cid}: done")
                continue
            if dt.datetime.now() > deadline and not args.mock:
                stopped = f"deadline {dl} reached before {cid}"
                print("STOP:", stopped)
                break
            system = F["C1"]["system_prompt"] if cond.get("system") else None
            print(f"=== {cid}: weights={cond['weights']} decoding={cond['decoding']}"
                  f"{' +system prompt' if system else ''}{' +steering' if cond.get('steer') else ''}")
            ctx.mock_strength = strength[cond["weights"]] + (0.4 if cond.get("steer") else 0)
            edit = E.AppliedEdit(ctx.model, plans[cond["weights"]]) if cond["weights"] != "base" and not args.mock else None
            steer = E.Steering(ctx.model, U, F["C2"]["layers"], F["C2"]["alpha_s"]) if cond.get("steer") and not args.mock else None
            for cm in (edit, steer):
                if cm:
                    cm.__enter__()
            try:
                for s in todo:
                    if dt.datetime.now() > deadline and not args.mock:
                        stopped = f"deadline {dl} reached during {cid} (before {s})"
                        break
                    rows, secs = R.generate_rows(ctx, data[s], s, decoding=cond["decoding"], seed=seed, system=system)
                    for r in rows:
                        r.update(condition=cid)
                    C.write_jsonl(out_dir / f"{cid}__{s}.jsonl", rows)
                    print(f"  {s:8s} loops {sum(r['loop'] for r in rows):3d}/{len(rows)}"
                          + (f"  acc {sum(r['correct'] for r in rows)}/{len(rows)}" if s.endswith("math") else "")
                          + f"  ({secs:.0f}s)")
                if need_ppl and not stopped:
                    ppl = {l: R.perplexity(ctx, ref[l]) for l in ("sv", "en")}
                    C.write_json(out_dir / f"{cid}__ppl.json", ppl)
                    print(f"  perplexity sv {ppl['sv']:.2f}  en {ppl['en']:.2f}")
            finally:
                for cm in (steer, edit):
                    if cm:
                        cm.__exit__(None, None, None)
            if stopped:
                print("STOP:", stopped)
                break
        C.write_json(out_dir / "run_status.json", dict(time=C.now(), stopped=stopped))
    summarize(out_dir, data, F, seed)


def load_cell(out_dir, cid, s):
    p = out_dir / f"{cid}__{s}.jsonl"
    return {r["id"]: r for r in C.load_jsonl(p)} if p.exists() else None


def summarize(out_dir, data, F, seed):
    nb = R.SPEC["test"]["bootstrap"]["n_boot"]
    conds = [c["id"] for c in R.SPEC["test"]["conditions"]]
    cells = {(c, s): load_cell(out_dir, c, s) for c in conds for s in SETS_FILES}
    have = {k: v for k, v in cells.items() if v}
    ppl = {c: json.loads((out_dir / f"{c}__ppl.json").read_text()) for c in conds if (out_dir / f"{c}__ppl.json").exists()}

    def ids(s):
        return [r["id"] for r in data[s]]

    def clusters(s):
        return [r.get("cluster", r["id"]) for r in data[s]]

    def vec(cid, s, key):
        if cid == "C5mean":
            parts = [cells[(f"C5s{k}", s)] for k in range(3) if cells.get((f"C5s{k}", s))]
            if not parts:
                return None
            return [float(np.mean([p[i][key] for p in parts])) for i in ids(s)]
        cell = cells.get((cid, s))
        return None if cell is None else [float(bool(cell[i][key])) for i in ids(s)]

    def compare(a, b, s, key):
        va, vb = vec(a, s, key), vec(b, s, key)
        if va is None or vb is None:
            return None
        d, lo, hi = M.cluster_bootstrap_diff(va, vb, clusters(s), n_boot=nb, seed=seed)
        out = dict(a=a, b=b, set=s, metric=key, diff=d, ci95=[lo, hi])
        if b != "C5mean" and a != "C5mean":
            out["mcnemar"] = mcnemar_exact([x > 0.5 for x in va], [x > 0.5 for x in vb])
        return out

    per_cell = {}
    for (c, s), cell in have.items():
        rows = list(cell.values())
        k = sum(r["loop"] for r in rows)
        e = dict(n=len(rows), loop=k / len(rows), loop_ci95=list(C.wilson_ci(k, len(rows))),
                 hit_limit=R.rate(rows, "hit_limit"), short=R.rate(rows, "short"),
                 median_tokens=M.median([r["n_new_tokens"] for r in rows]),
                 distinct2=float(np.mean([r["distinct2"] for r in rows])))
        if s.endswith("math"):
            e["acc"] = R.rate(rows, "correct")
        per_cell[f"{c}|{s}"] = e

    pairs = [("C3", "C0"), ("C3", "C5s0"), ("C3", "C5s1"), ("C3", "C5s2"), ("C3", "C5mean"), ("C3", "C9"),
             ("C3def", "C9"), ("C9", "C0"), ("C1", "C0"), ("C2", "C0"), ("C3", "C1"), ("C3", "C2"), ("C5mean", "C0")]
    comp = {"sv_open_loop": [x for a, b in pairs if (x := compare(a, b, "sv_open", "loop"))],
            "en_open_loop": [x for a, b in [("C3", "C0"), ("C3def", "C9")] if (x := compare(a, b, "en_open", "loop"))],
            "math_acc": [x for a, b, s in [("C3", "C0", "sv_math"), ("C3", "C0", "en_math"), ("C3def", "C9", "sv_math"),
                                           ("C3def", "C9", "en_math"), ("C5mean", "C0", "sv_math"),
                                           ("C1", "C0", "sv_math"), ("C2", "C0", "sv_math")]
                         if (x := compare(a, b, s, "correct"))]}

    def es(a, b):
        sa, sb = cells.get((a, "sv_open")), cells.get((b, "sv_open"))
        if not sa or not sb:
            return None
        ea, eb = cells.get((a, "en_open")), cells.get((b, "en_open"))
        return R.early_stop(list(sa.values()), list(ea.values()) if ea else None, list(sb.values()),
                            list(eb.values()) if eb else None)
    early = {f"{a} vs {b}": x for a, b in [("C3", "C0"), ("C3def", "C9"), ("C1", "C0"), ("C2", "C0"), ("C5s0", "C0")]
             if (x := es(a, b))}

    def find(lst, a, b, s=None):
        return next((x for x in lst if x["a"] == a and x["b"] == b and (s is None or x["set"] == s)), None)

    checks = {}
    c30, c35 = find(comp["sv_open_loop"], "C3", "C0"), find(comp["sv_open_loop"], "C3", "C5mean")
    if c30:
        h1 = dict(drop_vs_C0=c30["diff"], ci_vs_C5=c35["ci95"] if c35 else None)
        sup = c30["diff"] <= -0.20 and c35 is not None and c35["ci95"][1] < 0
        chal = c30["diff"] > -0.10 or (c35 is not None and c35["ci95"][1] >= 0)
        h1["mechanical"] = "supported" if sup else ("challenged" if chal else "neither")
        checks["H1prime"] = h1
    if ("C3", "en_open") in have and ("C0", "en_open") in have and "C3" in ppl and "C0" in ppl:
        en_l = find(comp["en_open_loop"], "C3", "C0")
        em = find(comp["math_acc"], "C3", "C0", "en_math")
        ppl_r = {l: ppl["C3"][l] / ppl["C0"][l] - 1 for l in ("sv", "en")}
        h2 = dict(en_loop_diff=en_l["diff"], en_math_diff=em["diff"] if em else None, ppl_rise=ppl_r,
                  early_stop=early.get("C3 vs C0", {}).get("passes"))
        h2["mechanical"] = "supported" if (en_l["diff"] <= 0 and (em is None or em["diff"] >= -0.05)
                                           and max(ppl_r.values()) <= 0.05 and h2["early_stop"]) else "challenged"
        checks["H2prime"] = h2
    c39, cd9 = find(comp["sv_open_loop"], "C3", "C9"), find(comp["sv_open_loop"], "C3def", "C9")
    if c39 or cd9:
        checks["practical"] = dict(C3_minus_C9=c39, C3def_minus_C9=cd9,
                                   C3_beats_C9=bool(c39 and c39["ci95"][1] < 0),
                                   C3def_beats_C9=bool(cd9 and cd9["ci95"][1] < 0))
    sm = find(comp["math_acc"], "C3", "C0", "sv_math")
    checks["H3prime_partial"] = dict(sv_math_diff=sm["diff"] if sm else None,
                                     sv_ppl_change=(ppl["C3"]["sv"] / ppl["C0"]["sv"] - 1) if {"C3", "C0"} <= set(ppl) else None,
                                     note="coherence ratings are done in the main thread (coherence_blind.jsonl)")

    # coherence sample (blind) and examples
    rng = random.Random(R.SPEC["test"]["coherence"]["seed"])
    sample_ids = sorted(rng.sample(ids("sv_open"), R.SPEC["test"]["coherence"]["n"]))
    c0 = cells.get(("C0", "sv_open"))
    blind, key = [], {}
    for c in R.SPEC["test"]["coherence"]["conditions"]:
        cell = cells.get((c, "sv_open"))
        if cell:
            for i in sample_ids:
                blind.append(dict(id=i, condition=c, prompt=cell[i]["prompt"], response=cell[i]["response"],
                                  loop=cell[i]["loop"], c0_loop=c0[i]["loop"] if c0 else None))
    rng.shuffle(blind)
    with open(out_dir / "coherence_blind.jsonl", "w", encoding="utf-8") as f:
        for j, b in enumerate(blind):
            bid = f"R{j + 1:03d}"
            key[bid] = dict(condition=b["condition"], id=b["id"], loop=b["loop"], c0_loop=b["c0_loop"])
            f.write(json.dumps(dict(blind_id=bid, prompt=b["prompt"], response=b["response"]), ensure_ascii=False) + "\n")
    C.write_json(out_dir / "coherence_key.json", key)
    (out_dir / "coherence_rubric.md").write_text(RUBRIC, encoding="utf-8")
    if key:
        sub = sorted(random.Random(seed + 7).sample(sorted(key), min(R.SPEC["test"]["coherence"]["author_subset"], len(key))))
        lines = ["# Author coherence ratings (blind, 20 items)", "", "Rubric: coherence_rubric.md. Write 1, 2 or 3 after "
                 "'Rating:'. Use machine translation if needed.", ""]
        bl = {json.loads(l)["blind_id"]: json.loads(l) for l in open(out_dir / "coherence_blind.jsonl", encoding="utf-8")}
        for b in sub:
            lines += [f"## {b}", f"Prompt: {bl[b]['prompt']}", "", "> " + bl[b]["response"][:1200].replace("\n", " "), "",
                      "Rating: ", ""]
        (out_dir / "coherence_author20.md").write_text("\n".join(lines), encoding="utf-8")
    c3 = cells.get(("C3", "sv_open"))
    if c0 and c3:
        ex = sorted(random.Random(seed + 3).sample(ids("sv_open"), 5))
        lines = ["# Before/after examples (C0 vs C3, sv_open test, fixed seed, first 500 characters)", ""]
        for i in ex:
            lines += [f"## {i}: {c0[i]['prompt']}", "", f"**C0** (loop: {c0[i]['loop']})", "",
                      "> " + c0[i]["response"][:500].replace("\n", " "), "", f"**C3** (loop: {c3[i]['loop']})", "",
                      "> " + c3[i]["response"][:500].replace("\n", " "), ""]
        (out_dir / "examples.md").write_text("\n".join(lines), encoding="utf-8")

    summary = dict(time=C.now(), frozen="configs/frozen.json", per_cell=per_cell, perplexity=ppl, comparisons=comp,
                   early_stop=early, checks=checks, coherence_items=len(key),
                   finished=sorted({c for c, _ in have}), missing=[f"{c}|{s}" for c, s in cells if not cells[(c, s)]
                                                                 and s in next(x["sets"] for x in R.SPEC["test"]["conditions"] if x["id"] == c)])
    C.write_json(out_dir / "summary.json", summary)

    pct = lambda x: "-" if x is None else f"{x * 100:.0f}%"  # noqa: E731
    md = ["# Test results (Step 6)", "", f"Frozen config: C3 = {F['C3']['name']} (layers {F['C3']['layers']}, "
          f"k={F['C3']['k']}, alpha={F['C3']['alpha']}); C2 alpha_s={F['C2']['alpha_s']}.", "",
          "| Condition | Set | n | Loop | 95% CI | Hit 512 | Short <30 | Median tokens | Distinct-2 | Math acc |",
          "|---|---|---:|---:|---|---:|---:|---:|---:|---:|"]
    for c in conds:
        for s in SETS_FILES:
            e = per_cell.get(f"{c}|{s}")
            if e:
                md.append(f"| {c} | {s} | {e['n']} | {pct(e['loop'])} | {e['loop_ci95'][0]*100:.0f}-{e['loop_ci95'][1]*100:.0f}% "
                          f"| {pct(e['hit_limit'])} | {pct(e['short'])} | {e['median_tokens']:.0f} | {e['distinct2']:.2f} "
                          f"| {pct(e.get('acc'))} |")
    md += ["", "Perplexity (teacher-forced): " + ", ".join(f"{c}: sv {v['sv']:.2f} / en {v['en']:.2f}" for c, v in ppl.items()),
           "", "## Paired comparisons (difference a - b; cluster bootstrap 95% CI; exact McNemar p)", "",
           "| Metric | a | b | Set | Diff | 95% CI | McNemar p |", "|---|---|---|---|---:|---|---:|"]
    for name, lst in comp.items():
        for x in lst:
            p = x.get("mcnemar", {}).get("p")
            md.append(f"| {name} | {x['a']} | {x['b']} | {x['set']} | {x['diff']*100:+.1f} pts | "
                      f"{x['ci95'][0]*100:+.1f} to {x['ci95'][1]*100:+.1f} | {'-' if p is None else f'{p:.3g}'} |")
    md += ["", "## Early-stop checks", ""]
    for k, v in early.items():
        md.append(f"- {k}: {'pass' if v['passes'] else 'FAIL'} " + json.dumps({a: round(b, 3) if isinstance(b, float) else b
                                                                               for a, b in v.items()}))
    md += ["", "## Mechanical hypothesis checks (thresholds from Deviations 4-5; interpretation at checkpoint b)", "",
           "```", json.dumps(checks, indent=2, default=str), "```", "",
           f"Coherence items written: {len(key)} (coherence_blind.jsonl). Finished conditions: {summary['finished']}. "
           f"Missing cells: {summary['missing'] or 'none'}.", ""]
    (out_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
