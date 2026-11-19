"""Step 3: pilot and model choice (docs/02_hypothesis.md, section 2.5 and Deviation 2).

Usage:  python scripts/02_pilot.py            (all three candidates)
        python scripts/02_pilot.py --mock     (no model download; tests the pipeline only)

For each candidate model: 40 Swedish dev prompts (first 40 of data/sv_open_dev.jsonl), default chat
template, greedy decoding, max 256 new tokens. Each response is classified with lingua (sv/en/nb/nn/da/de;
under 20 characters = failure). Applies the pre-registered gate:

  lowest Swedish rate <= 75%         -> GO
  75% < lowest Swedish rate <= 90%   -> GO, but report small headroom (Deviation 2)
  every candidate > 90%              -> failure absent; switch target to Scandinavian leakage

Outputs in results/pilot/:
  <model>_responses.jsonl   every prompt, response and language label
  summary.json              rates, 95% Wilson CIs, language counts, gate decision
  summary.md                same as a readable table
  hand_check.md             10 Swedish-labelled responses per model (fixed seed) for reading by hand
Also writes results/model_revisions.json, results/env.json and appends to results/feedback_log.jsonl.
"""
import argparse
import random
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

N_PILOT = 40
MAX_NEW_TOKENS = 256
HAND_CHECK_SEED = 7
OUT = C.RESULTS / "pilot"


def gate(rates):
    lowest = min(rates.values())
    if lowest <= 0.75:
        return "GO", "Lowest Swedish rate <= 75%: failure is present, run the experiment on this model."
    if lowest <= 0.90:
        return "GO_SMALL_HEADROOM", ("Lowest Swedish rate is between 75% and 90%: run the experiment on this "
                                     "model and state in the report that headroom is small (Deviation 2).")
    return "SWITCH", ("Every candidate is above 90% Swedish: the failure is absent at this scale. Report this "
                      "and switch the target to Scandinavian leakage.")


def mock_generate(prompts):
    out = []
    for i, p in enumerate(prompts):
        if i % 3 == 0:
            r = "Sure! Here is a short explanation in English of the topic you asked about."
        else:
            r = "Självklart! Här kommer en kort förklaring på svenska av det du frågade om."
        out.append(dict(response=r, n_new_tokens=20, hit_limit=False))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true", help="skip model download, use fake responses")
    ap.add_argument("--models", nargs="*", help="subset of candidate names to run")
    ap.add_argument("--batch-size", type=int, default=8)
    args = ap.parse_args()

    prompts = C.load_jsonl(C.DATA / "sv_open_dev.jsonl")[:N_PILOT]
    cands = C.load_model_configs()["candidates"]
    if args.models:
        cands = [c for c in cands if c["name"] in args.models]

    out_dir = OUT if not args.mock else C.RESULTS / "pilot_mock"
    out_dir.mkdir(parents=True, exist_ok=True)
    env = C.env_info()
    if not args.mock:
        C.write_json(C.RESULTS / "env.json", env)
        device = C.get_device()
        print(f"Device: {device} | torch {env.get('torch')} | transformers {env.get('transformers')}")

    revisions_path = C.RESULTS / "model_revisions.json"
    revisions = {}
    if revisions_path.exists():
        import json
        revisions = json.loads(revisions_path.read_text(encoding="utf-8"))

    summary = dict(time=C.now(), n_prompts=N_PILOT, prompt_file="data/sv_open_dev.jsonl (first 40)",
                   decoding=dict(do_sample=False, max_new_tokens=MAX_NEW_TOKENS, repetition_penalty=1.0),
                   language_id="lingua, restricted to sv/en/nb/nn/da/de; <20 chars = failure",
                   models={})
    hand = ["# Pilot hand check", "",
            "10 responses per model that lingua labelled Swedish (fixed seed). For each, mark whether the "
            "Swedish is readable (Y/N). The plan requires this for the model with the lowest Swedish rate.", ""]

    for c in cands:
        name = c["name"]
        print(f"\n=== {name} ({c['repo_id']}) ===")
        t0 = time.time()
        if args.mock:
            sha = "mock"
            gens = mock_generate([p["text"] for p in prompts])
        else:
            sha = C.resolve_revision(c["repo_id"], c.get("revision"))
            revisions[name] = dict(repo_id=c["repo_id"], revision=sha, resolved_at=C.now())
            C.write_json(revisions_path, revisions)
            tok, model = C.load_model(c["repo_id"], sha, device)
            texts = [C.chat_prompt(tok, p["text"], template_kwargs=c.get("template_kwargs")) for p in prompts]
            gens = C.generate(tok, model, texts, max_new_tokens=MAX_NEW_TOKENS, batch_size=args.batch_size)
            del model
            C.log_feedback("pilot: model choice (sec. 2.5)", name, n_prompts=N_PILOT, condition="C0",
                           note=f"revision {sha}")

        rows = []
        for p, g in zip(prompts, gens):
            rows.append(dict(id=p["id"], cluster=p["cluster"], prompt=p["text"], response=g["response"],
                             lang=C.detect_lang(g["response"]), n_new_tokens=g["n_new_tokens"],
                             hit_limit=g["hit_limit"]))
        C.write_jsonl(out_dir / f"{name}_responses.jsonl", rows)

        counts = Counter(r["lang"] for r in rows)
        k = counts.get("sv", 0)
        lo, hi = C.wilson_ci(k, len(rows))
        summary["models"][name] = dict(repo_id=c["repo_id"], revision=sha, swedish_rate=k / len(rows),
                                       swedish_ci95=[lo, hi], lang_counts=dict(counts),
                                       hit_token_limit=sum(r["hit_limit"] for r in rows),
                                       seconds=round(time.time() - t0, 1))
        print(f"Swedish rate {k}/{len(rows)} = {k/len(rows):.1%}  (95% CI {lo:.0%}-{hi:.0%})  counts {dict(counts)}")

        sv_rows = [r for r in rows if r["lang"] == "sv"]
        pick = random.Random(HAND_CHECK_SEED).sample(sv_rows, min(10, len(sv_rows)))
        hand += [f"## {name}  (Swedish rate {k/len(rows):.0%})", ""]
        for r in pick:
            resp = r["response"].replace("\n", " ")[:600]
            hand += [f"**{r['id']}** prompt: {r['prompt']}", "", f"> {resp}", "", "Readable: [ ]", ""]
        non_sv = [r for r in rows if r["lang"] != "sv"][:3]
        if non_sv:
            hand += ["Non-Swedish examples (first 3, for context):", ""]
            for r in non_sv:
                hand += [f"- **{r['id']}** [{r['lang']}] {r['response'][:200].replace(chr(10), ' ')}"]
            hand.append("")

    rates = {n: m["swedish_rate"] for n, m in summary["models"].items()}
    decision, reason = gate(rates)
    chosen = min(rates, key=rates.get)
    summary["gate"] = dict(decision=decision, reason=reason, lowest_rate_model=chosen,
                           lowest_rate=rates[chosen],
                           note="Final model choice also requires readable Swedish in hand_check.md "
                                "and is confirmed in the main thread before Step 4.")
    C.write_json(out_dir / "summary.json", summary)
    (out_dir / "hand_check.md").write_text("\n".join(hand), encoding="utf-8")

    md = ["# Pilot summary", "", f"{N_PILOT} Swedish dev prompts, greedy, max {MAX_NEW_TOKENS} new tokens.", "",
          "| Model | Revision | Swedish rate | 95% CI | Language counts | Hit token limit |",
          "|---|---|---:|---|---|---:|"]
    for n, m in summary["models"].items():
        md.append(f"| {n} | `{m['revision'][:10]}` | {m['swedish_rate']:.1%} | "
                  f"{m['swedish_ci95'][0]:.0%}-{m['swedish_ci95'][1]:.0%} | {m['lang_counts']} | {m['hit_token_limit']} |")
    md += ["", f"**Gate:** {decision}. {reason}", f"Lowest Swedish rate: **{chosen}** ({rates[chosen]:.1%}).", ""]
    (out_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")

    print("\n" + "\n".join(md))
    print(f"Files written to {out_dir.relative_to(C.ROOT)}/. Next: read hand_check.md for {chosen}.")


if __name__ == "__main__":
    main()
