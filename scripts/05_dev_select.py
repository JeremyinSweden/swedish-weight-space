"""Step 5: dev selection and freeze (Deviation 5, items 5-6).

Usage:  python scripts/05_dev_select.py          (about 20-30 min on the M1 Pro; resumable)
        python scripts/05_dev_select.py --mock

Passes (each logged in results/feedback_log.jsonl):
  1. C0 on dev (fresh, same batch size as all later passes)
  2. default config (paper placement, 0 feedback passes used to choose it)
  3-8. the 6 grid configs fixed in configs/step4_6.json
  9-10. steering C2 at the selected layers, alpha_s in {1, 2}
Selection rule and fallback are fixed in configs/step4_6.json. Writes configs/frozen.json and the edit diffs
(column indices + delta values, never a full checkpoint) to results/edits/.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import edits as E  # noqa: E402
import runner as R  # noqa: E402

DEV = R.SPEC["dev"]


def file_sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    args = ap.parse_args()
    sfx = "_mock" if args.mock else ""
    out_dir, edit_dir = C.RESULTS / f"dev{sfx}", C.RESULTS / f"edits{sfx}"
    dir_dir = C.RESULTS / f"direction{sfx}"
    out_dir.mkdir(parents=True, exist_ok=True)
    edit_dir.mkdir(parents=True, exist_ok=True)
    U = np.load(dir_dir / "u.npz")["U"].astype(np.float64)
    dsum = json.loads((dir_dir / "summary.json").read_text(encoding="utf-8"))
    top2 = dsum["top2"]
    sv = C.load_jsonl(C.DATA / "sv_open_dev.jsonl")[:40]
    en = C.load_jsonl(C.DATA / "en_open_dev.jsonl")[:40]
    ctx = R.Ctx(mock=args.mock).load()
    seed = R.SPEC["seed"]

    def run_pass(name, purpose, condition, strength=0.0):
        p_sv, p_en = out_dir / f"{name}__sv_open.jsonl", out_dir / f"{name}__en_open.jsonl"
        if p_sv.exists() and p_en.exists():
            print(f"  {name}: done earlier, loading")
            return C.load_jsonl(p_sv), C.load_jsonl(p_en)
        ctx.mock_strength = strength
        rs, ts = R.generate_rows(ctx, sv, "sv_open", seed=seed)
        re_, te = R.generate_rows(ctx, en, "en_open", seed=seed)
        C.write_jsonl(p_sv, rs)
        C.write_jsonl(p_en, re_)
        if not args.mock:
            C.log_feedback(purpose, ctx.name, n_prompts=80, condition=condition, note=f"{name}; revision {ctx.revision}")
        print(f"  {name}: sv loops {sum(r['loop'] for r in rs)}/40, en loops {sum(r['loop'] for r in re_)}/40 "
              f"({ts + te:.0f}s)")
        return rs, re_

    print("Pass 1: C0 on dev")
    c0_sv, c0_en = run_pass("C0", "Step 5 dev: C0 baseline (batch size of Steps 4-6)", "C0")
    c0_en_loop = R.rate(c0_en, "loop")

    configs = [dict(DEV["default_config"])] + [dict(g) for g in DEV["grid"]]
    for c in configs:
        c["layers"] = top2 if c["layers"] == "top2" else list(c["layers"])
    all_layers = sorted({l for c in configs for l in c["layers"]})
    Wcache = {l: np.zeros((896, 4864)) for l in all_layers} if args.mock else E.read_weights(ctx.model, all_layers)
    if args.mock:
        rng = np.random.default_rng(1)
        Wcache = {l: rng.standard_normal((896, 4864)) * 0.02 for l in all_layers}

    table = []
    for i, c in enumerate(configs):
        plan, frob = E.edit_plan(Wcache, U, c["layers"], c["k"], c["alpha"])
        print(f"Pass {i + 2}: C3 config {c['name']} layers={c['layers']} k={c['k']} alpha={c['alpha']} |dW|={frob:.3f}")
        strength = min(0.9, c["alpha"] * c["k"] / 600)
        if args.mock:
            rs, re_ = run_pass(c["name"], "", "C3", strength)
        else:
            with E.AppliedEdit(ctx.model, plan):
                rs, re_ = run_pass(c["name"], f"Step 5 dev: C3 config {c['name']}", "C3")
        es = R.early_stop(rs, re_, c0_sv, c0_en)
        table.append(dict(c, frob=frob, sv_loop=R.rate(rs, "loop"), en_loop=R.rate(re_, "loop"),
                          en_ok=R.rate(re_, "loop") <= c0_en_loop, early_stop=es,
                          eligible=(R.rate(re_, "loop") <= c0_en_loop) and es["passes"]))

    eligible = [t for t in table if t["eligible"]]
    flag = None
    if eligible:
        sel = min(eligible, key=lambda t: (t["sv_loop"], t["frob"]))
    else:
        es_ok = [t for t in table if t["early_stop"]["passes"]]
        sel = min(es_ok, key=lambda t: (t["sv_loop"], t["frob"])) if es_ok else table[0]
        flag = "no config met all constraints; fallback rule used"
    print(f"Selected C3 config: {sel['name']} (sv loop {sel['sv_loop']:.0%}, en loop {sel['en_loop']:.0%})"
          + (f"  [{flag}]" if flag else ""))

    steer = []
    for j, a in enumerate(DEV["steering_alphas"]):
        name = f"C2_a{a:g}"
        print(f"Pass {len(configs) + 2 + j}: steering {name} at layers {sel['layers']}")
        if args.mock:
            rs, re_ = run_pass(name, "", "C2", min(0.9, 0.3 * a))
        else:
            with E.Steering(ctx.model, U, sel["layers"], a):
                rs, re_ = run_pass(name, f"Step 5 dev: C2 steering alpha_s={a}", "C2")
        es = R.early_stop(rs, re_, c0_sv, c0_en)
        steer.append(dict(name=name, alpha_s=a, sv_loop=R.rate(rs, "loop"), en_loop=R.rate(re_, "loop"),
                          early_stop=es, eligible=(R.rate(re_, "loop") <= c0_en_loop) and es["passes"]))
    s_el = [s for s in steer if s["eligible"]] or [s for s in steer if s["early_stop"]["passes"]] or steer[:1]
    s_sel = min(s_el, key=lambda s: (s["sv_loop"], s["alpha_s"]))

    # save diffs: selected edit, default edit, and the three random controls (same S, same column norms)
    sel_plan, _ = E.edit_plan(Wcache, U, sel["layers"], sel["k"], sel["alpha"])
    E.save_plan(edit_dir / "C3_selected.npz", sel_plan, dict(sel, frob=sel["frob"]))
    def_c = table[0]
    E.save_plan(edit_dir / "C3_default.npz", E.edit_plan(Wcache, U, def_c["layers"], def_c["k"], def_c["alpha"])[0],
                dict(def_c))
    rnd_frob = {}
    for s in (0, 1, 2):
        p, f = E.edit_plan(Wcache, U, sel["layers"], sel["k"], sel["alpha"], random_seed=s)
        E.save_plan(edit_dir / f"C5_seed{s}.npz", p, dict(sel, random_seed=s))
        rnd_frob[s] = f

    n_passes = 1 + len(configs) + len(steer)
    frozen = dict(
        frozen_at=C.now(), model=ctx.name, repo_id=ctx.mc["repo_id"], revision=ctx.revision,
        spec="configs/step4_6.json + docs/02_hypothesis.md Deviation 5",
        direction_file=f"results/direction{sfx}/u.npz",
        direction_sha256=file_sha(dir_dir / "u.npz"), top2_layers=top2,
        C3=dict(name=sel["name"], layers=sel["layers"], k=sel["k"], alpha=sel["alpha"], frob=sel["frob"],
                diff_file=f"results/edits{sfx}/C3_selected.npz"),
        C3_default=dict(layers=def_c["layers"], k=def_c["k"], alpha=def_c["alpha"], frob=def_c["frob"]),
        C5=dict(seeds=[0, 1, 2], same_columns_as_C3=True, frob=rnd_frob,
                diff_files=[f"results/edits{sfx}/C5_seed{s}.npz" for s in (0, 1, 2)]),
        C2=dict(layers=sel["layers"], alpha_s=s_sel["alpha_s"]),
        C1=dict(system_prompt=R.SPEC["c1_system_prompt"]),
        C9=dict(decoding=R.decoding_kwargs("shipped_defaults")),
        selection_flag=flag, feedback_passes_dev=n_passes,
        feedback_passes_by_method=dict(C3_default=0, C3_selected=1 + len(configs), C2=1 + len(configs) + len(steer)),
        batch_size=R.SPEC["batch_size"], max_new_tokens=R.SPEC["max_new_tokens"], seed=seed,
        test_plan=R.SPEC["test"],
        data_sha256={n: file_sha(C.DATA / n) for n in ["sv_open_test.jsonl", "en_open_test.jsonl", "sv_math_test.jsonl",
                                                     "en_math_test.jsonl", "sv_ref_test.jsonl", "en_ref_test.jsonl"]},
        dev_table=[{k: v for k, v in t.items()} for t in table], dev_steering=steer)
    C.write_json(C.CONFIGS / f"frozen{sfx}.json", frozen)

    md = ["# Dev selection (Step 5)", "", f"C0 dev: sv_open loops {R.rate(c0_sv, 'loop'):.0%}, en_open loops "
          f"{c0_en_loop:.0%}, short (<30 tokens) sv {R.rate(c0_sv, 'short'):.0%} / en {R.rate(c0_en, 'short'):.0%}", "",
          "| Config | Layers | k | alpha | Frobenius norm | sv_open loop | en_open loop | en <= C0? | Early-stop | Eligible |",
          "|---|---|---:|---:|---:|---:|---:|---|---|---|"]
    for t in table:
        md.append(f"| {t['name']} | {t['layers']} | {t['k']} | {t['alpha']} | {t['frob']:.3f} | {t['sv_loop']:.0%} | "
                  f"{t['en_loop']:.0%} | {'yes' if t['en_ok'] else 'no'} | {'pass' if t['early_stop']['passes'] else 'FAIL'} "
                  f"| {'yes' if t['eligible'] else 'no'} |")
    md += ["", "| Steering | alpha_s | sv_open loop | en_open loop | Early-stop | Eligible |", "|---|---:|---:|---:|---|---|"]
    for s in steer:
        md.append(f"| {s['name']} | {s['alpha_s']} | {s['sv_loop']:.0%} | {s['en_loop']:.0%} | "
                  f"{'pass' if s['early_stop']['passes'] else 'FAIL'} | {'yes' if s['eligible'] else 'no'} |")
    md += ["", f"**Selected C3:** {sel['name']} (layers {sel['layers']}, k={sel['k']}, alpha={sel['alpha']})"
           + (f" -- {flag}" if flag else ""), f"**Selected C2:** alpha_s={s_sel['alpha_s']} at layers {sel['layers']}",
           f"Dev feedback passes: {n_passes}. Frozen config: configs/frozen{sfx}.json", ""]
    (out_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n" + "\n".join(md))
    print("NEXT: commit the frozen config BEFORE running the test:\n"
          "  git add -A && git commit -m \"Freeze config before test run\"")


if __name__ == "__main__":
    main()
