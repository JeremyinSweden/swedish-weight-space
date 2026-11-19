"""Step 3b: pilot 2 (docs/02_hypothesis.md, Deviation 4). Dev data only.

Usage:  python scripts/03_pilot2.py            (both models, both decodings)
        python scripts/03_pilot2.py --mock     (fake model, tests the pipeline only)
        python scripts/03_pilot2.py --summary-only   (recompute tables from saved responses)

Questions:
  - Do Swedish loops survive the models' recommended decoding settings?  (prediction P2)
  - Do the models loop more in Swedish than in English?                  (prediction P1)
  - Gate: Qwen2.5-0.5B Swedish loop rate (sv_open, greedy) >= 40% -> edit experiment on Qwen2.5;
          else Qwen3-0.6B if it meets the same bar; else stop.

Cells: 2 models x 2 decodings x 4 prompt sets (40 sv_open, 40 parallel en_open, 60 sv_math, 60 en_math dev),
max 512 new tokens. Each cell is saved as soon as it finishes; a re-run skips finished cells
(use --force to regenerate).

Loop = some lowercased word 8-gram occurs >= 3 times. Secondary: response reaches max_new_tokens.

Outputs in results/pilot2/:
  <model>__<decoding>__<set>.jsonl   prompt, response, loop flag, math correctness
  summary.json / summary.md          tables, gate, P1/P2 checks (numbers only; decisions are made elsewhere)
  samples.md                         2 random sv_open responses per model x decoding (fixed seed)
Also appends to results/feedback_log.jsonl.
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import metrics as M  # noqa: E402

CFG = json.loads((C.CONFIGS / "pilot2.json").read_text(encoding="utf-8"))
SETS = ["sv_open", "en_open", "sv_math", "en_math"]
DECODINGS = ["greedy", "recommended"]


def load_sets():
    n_open, n_math = CFG["n_open"], CFG["n_math"]
    data = {
        "sv_open": C.load_jsonl(C.DATA / "sv_open_dev.jsonl")[:n_open],
        "en_open": C.load_jsonl(C.DATA / "en_open_dev.jsonl")[:n_open],
        "sv_math": C.load_jsonl(C.DATA / "sv_math_dev.jsonl")[:n_math],
        "en_math": C.load_jsonl(C.DATA / "en_math_dev.jsonl")[:n_math],
    }
    assert [r["id"] for r in data["sv_open"]] == [r["id"] for r in data["en_open"]], "open sets not parallel"
    assert [r["id"] for r in data["sv_math"]] == [r["id"] for r in data["en_math"]], "math sets not parallel"
    return data


def decoding_settings(dec, model_name):
    d = CFG["decodings"][dec]
    s = d.get(model_name, d.get("all"))
    return {k: v for k, v in s.items() if not k.startswith("_")}


def cell_path(out_dir, model, dec, set_name):
    return out_dir / f"{model}__{dec}__{set_name}.jsonl"


def cell_seed(mi, di, si):
    return CFG["seed"] + 1000 * mi + 100 * di + si


def mock_generate(prompts, set_name, dec, seed, max_new_tokens):
    rng = random.Random(seed)
    p_loop = {"sv": 0.7, "en": 0.15}[set_name[:2]] * (0.5 if dec == "recommended" else 1.0)
    out = []
    for p in prompts:
        if rng.random() < p_loop:
            text = "Detta är en del av en ordning som är en ordning av ord. " * 20
            n, hit = max_new_tokens, True
        else:
            text = "Svaret är kort och tydligt, och det slutar här. Svaret blir " + str(rng.randint(1, 99))
            n, hit = 15, False
        out.append(dict(response=text, n_new_tokens=n, hit_limit=hit))
    return out


def build_rows(items, gens, set_name):
    rows = []
    for it, g in zip(items, gens):
        r = dict(id=it["id"], prompt=it["text"], response=g["response"], n_new_tokens=g["n_new_tokens"],
                 hit_limit=g["hit_limit"], loop=M.is_loop(g["response"]),
                 max_8gram_count=M.max_ngram_count(g["response"]))
        if "cluster" in it:
            r["cluster"] = it["cluster"]
        if set_name.endswith("math"):
            r.update(answer=it["answer"], template=it["template"],
                     extracted=M.extract_last_number(g["response"]),
                     correct=M.math_correct(g["response"], it["answer"]))
        rows.append(r)
    return rows


def run(args, out_dir, data):
    device = None if args.mock else C.get_device()
    if not args.mock:
        C.write_json(out_dir / "env.json", C.env_info())
        print(f"Device: {device}")
    repo_defaults = {}
    for mi, name in enumerate(CFG["models"]):
        todo = [(di, dec, si, s) for di, dec in enumerate(DECODINGS) for si, s in enumerate(SETS)
                if args.force or not cell_path(out_dir, name, dec, s).exists()]
        if not todo:
            print(f"{name}: all cells done, skipping")
            continue
        mc = C.model_config(name)
        tok = model = None
        if not args.mock:
            rev = C.pinned_revision(name)
            print(f"\n=== {name} ({mc['repo_id']} @ {rev[:10]}) ===")
            tok, model = C.load_model(mc["repo_id"], rev, device)
            gc = model.generation_config.to_dict()
            repo_defaults[name] = {k: gc.get(k) for k in ("do_sample", "temperature", "top_p", "top_k",
                                                         "min_p", "repetition_penalty")}
        n_new = {dec: 0 for dec in DECODINGS}
        for di, dec, si, s in todo:
            settings = decoding_settings(dec, name)
            seed = cell_seed(mi, di, si)
            items = data[s]
            t0 = time.time()
            if args.mock:
                gens = mock_generate(items, s, dec, seed, CFG["max_new_tokens"])
            else:
                texts = [C.chat_prompt(tok, it["text"], template_kwargs=mc.get("template_kwargs")) for it in items]
                gens = C.generate(tok, model, texts, max_new_tokens=CFG["max_new_tokens"],
                                  batch_size=args.batch_size, seed=seed, **settings)
            rows = build_rows(items, gens, s)
            for r in rows:
                r.update(model=name, decoding=dec, settings=settings, seed=seed)
            C.write_jsonl(cell_path(out_dir, name, dec, s), rows)
            n_new[dec] += len(rows)
            loops = sum(r["loop"] for r in rows)
            print(f"  {dec:11s} {s:8s} loops {loops:3d}/{len(rows)}  ({time.time() - t0:.0f}s)")
        if not args.mock:
            for dec, n in n_new.items():
                if n:
                    C.log_feedback("pilot 2: loop precondition + decoding check (Deviation 4)", name,
                                   n_prompts=n, condition="C0" if dec == "greedy" else "C9",
                                   note=f"decoding={dec}, revision {C.pinned_revision(name)}")
            del model
    if repo_defaults:
        C.write_json(out_dir / "repo_generation_defaults.json", repo_defaults)


def rate(rows, key):
    k = sum(bool(r[key]) for r in rows)
    lo, hi = C.wilson_ci(k, len(rows))
    return dict(k=k, n=len(rows), rate=k / len(rows) if rows else float("nan"), ci95=[lo, hi])


def summarize(out_dir):
    cells, missing = {}, []
    for name in CFG["models"]:
        for dec in DECODINGS:
            for s in SETS:
                p = cell_path(out_dir, name, dec, s)
                if not p.exists():
                    missing.append(p.name)
                    continue
                rows = C.load_jsonl(p)
                non_loop = [r["n_new_tokens"] for r in rows if not r["loop"]]
                c = dict(loop=rate(rows, "loop"), hit_limit=rate(rows, "hit_limit"),
                         median_tokens_all=M.median([r["n_new_tokens"] for r in rows]),
                         median_tokens_non_loop=M.median(non_loop), n_non_loop=len(non_loop))
                if s.endswith("math"):
                    c["math_acc"] = rate(rows, "correct")
                    lp = [r for r in rows if r["loop"]]
                    nl = [r for r in rows if not r["loop"]]
                    c["math_acc_looping"] = rate(lp, "correct") if lp else None
                    c["math_acc_non_looping"] = rate(nl, "correct") if nl else None
                cells[f"{name}|{dec}|{s}"] = c
    if missing:
        print("Missing cells (run without --summary-only first):", ", ".join(missing))
        return None

    # P1: sv vs en loop rate, greedy, paired by item (open: resample by topic cluster)
    p1 = {}
    for name in CFG["models"]:
        for kind in ("open", "math"):
            sv = C.load_jsonl(cell_path(out_dir, name, "greedy", f"sv_{kind}"))
            en = C.load_jsonl(cell_path(out_dir, name, "greedy", f"en_{kind}"))
            clusters = [r.get("cluster", r["id"]) for r in sv]
            d, lo, hi = M.cluster_bootstrap_diff([r["loop"] for r in sv], [r["loop"] for r in en], clusters,
                                                 seed=CFG["seed"])
            p1[f"{name}|{kind}"] = dict(sv_minus_en=d, ci95=[lo, hi], meets_20pt=d >= 0.20)

    # P2: recommended vs greedy on Swedish prompts (paired by item)
    p2 = {}
    for name in CFG["models"]:
        for kind in ("open", "math"):
            g = C.load_jsonl(cell_path(out_dir, name, "greedy", f"sv_{kind}"))
            r = C.load_jsonl(cell_path(out_dir, name, "recommended", f"sv_{kind}"))
            clusters = [x.get("cluster", x["id"]) for x in g]
            d, lo, hi = M.cluster_bootstrap_diff([x["loop"] for x in r], [x["loop"] for x in g], clusters,
                                                 seed=CFG["seed"])
            rec_rate = sum(x["loop"] for x in r) / len(r)
            p2[f"{name}|{kind}"] = dict(recommended_minus_greedy=d, ci95=[lo, hi],
                                        reduced=d < 0, removed=rec_rate == 0.0)

    gcfg = CFG["gate"]
    key = lambda m: f"{m}|{gcfg['decoding']}|sv_{gcfg['set']}"  # noqa: E731
    main_rate = cells[key(gcfg["main"])]["loop"]["rate"]
    ref_rate = cells[key(gcfg["reference"])]["loop"]["rate"]
    if main_rate >= gcfg["min_sv_loop_rate"]:
        gate = dict(outcome="main", model=gcfg["main"])
    elif ref_rate >= gcfg["min_sv_loop_rate"]:
        gate = dict(outcome="reference", model=gcfg["reference"])
    else:
        gate = dict(outcome="stop", model=None)
    gate.update(rule=f"sv_{gcfg['set']} loop rate under {gcfg['decoding']} >= {gcfg['min_sv_loop_rate']:.0%}",
                main_rate=main_rate, reference_rate=ref_rate)

    summary = dict(time=C.now(), spec="docs/02_hypothesis.md Deviation 4", config=CFG, cells=cells,
                   P1=p1, P2=p2, gate=gate)
    C.write_json(out_dir / "summary.json", summary)

    pct = lambda x: "n/a" if x is None else f"{x['rate']:.0%} ({x['k']}/{x['n']})"  # noqa: E731
    md = ["# Pilot 2 summary", "",
          f"Dev only. max_new_tokens {CFG['max_new_tokens']}. Loop = a lowercased word 8-gram occurs >= 3 times.",
          "Median tokens = median new tokens of non-looping responses (baseline for the early-stop check).", "",
          "| Model | Decoding | Set | Loop rate | 95% CI | Hit 512 limit | Median tokens (non-loop) | Math acc |",
          "|---|---|---|---:|---|---:|---:|---:|"]
    for name in CFG["models"]:
        for dec in DECODINGS:
            for s in SETS:
                c = cells[f"{name}|{dec}|{s}"]
                md.append(f"| {name} | {dec} | {s} | {pct(c['loop'])} | {c['loop']['ci95'][0]:.0%}-{c['loop']['ci95'][1]:.0%} "
                          f"| {pct(c['hit_limit'])} | {c['median_tokens_non_loop']:.0f} (n={c['n_non_loop']}) "
                          f"| {pct(c.get('math_acc')) if s.endswith('math') else '-'} |")
    md += ["", "## Math accuracy split by looping (paper-style strata, greedy and recommended)", "",
           "| Model | Decoding | Set | Acc. when looping | Acc. when not looping |", "|---|---|---|---:|---:|"]
    for name in CFG["models"]:
        for dec in DECODINGS:
            for s in ("sv_math", "en_math"):
                c = cells[f"{name}|{dec}|{s}"]
                md.append(f"| {name} | {dec} | {s} | {pct(c['math_acc_looping'])} | {pct(c['math_acc_non_looping'])} |")
    md += ["", "## P1: Swedish minus English loop rate (greedy, paired, cluster bootstrap 95% CI)", "",
           "| Model | Prompts | sv - en | 95% CI | >= 20 points? |", "|---|---|---:|---|---|"]
    for k, v in p1.items():
        m, kind = k.split("|")
        md.append(f"| {m} | {kind} | {v['sv_minus_en']*100:+.0f} pts | {v['ci95'][0]*100:+.0f} to {v['ci95'][1]*100:+.0f} "
                  f"| {'yes' if v['meets_20pt'] else 'no'} |")
    md += ["", "## P2: recommended minus greedy loop rate on Swedish prompts (paired)", "",
           "| Model | Prompts | rec - greedy | 95% CI | Reduced? | Removed? |", "|---|---|---:|---|---|---|"]
    for k, v in p2.items():
        m, kind = k.split("|")
        md.append(f"| {m} | {kind} | {v['recommended_minus_greedy']*100:+.0f} pts | {v['ci95'][0]*100:+.0f} to "
                  f"{v['ci95'][1]*100:+.0f} | {'yes' if v['reduced'] else 'no'} | {'yes' if v['removed'] else 'no'} |")
    md += ["", f"## Gate ({gate['rule']})", "",
           f"Qwen2.5 rate {main_rate:.0%}, Qwen3 rate {ref_rate:.0%}. Mechanical outcome: **{gate['outcome']}**"
           f"{' (' + gate['model'] + ')' if gate['model'] else ''}. To be confirmed at checkpoint (a2).", ""]
    (out_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")

    rng = random.Random(CFG["seed"])
    sm = ["# Pilot 2 samples", "", "2 random sv_open responses per model x decoding (fixed seed), first 500 characters.", ""]
    for name in CFG["models"]:
        for dec in DECODINGS:
            rows = C.load_jsonl(cell_path(out_dir, name, dec, "sv_open"))
            sm += [f"## {name} / {dec}", ""]
            for r in rng.sample(rows, 2):
                sm += [f"**{r['id']}** (loop: {r['loop']}) {r['prompt']}", "",
                       "> " + r["response"][:500].replace("\n", " "), ""]
    (out_dir / "samples.md").write_text("\n".join(sm), encoding="utf-8")
    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--force", action="store_true", help="regenerate finished cells")
    ap.add_argument("--summary-only", action="store_true")
    ap.add_argument("--batch-size", type=int, default=16)
    args = ap.parse_args()
    out_dir = C.RESULTS / ("pilot2_mock" if args.mock else "pilot2")
    out_dir.mkdir(parents=True, exist_ok=True)
    data = load_sets()
    if not args.summary_only:
        run(args, out_dir, data)
    md = summarize(out_dir)
    if md:
        print("\n" + md)
        print(f"\nFiles in {out_dir.relative_to(C.ROOT)}/")


if __name__ == "__main__":
    main()
