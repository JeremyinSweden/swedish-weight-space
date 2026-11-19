"""Step 4: loop direction from the model's own responses (Deviation 4/5, plan.md handoff item 1).

Usage:  python scripts/04_direction.py          (about 5-8 min on the M1 Pro)
        python scripts/04_direction.py --mock   (numpy-only pipeline test)

1. Greedy responses to all 150 prompts in data/contrast_sv.jsonl (512 new tokens).
2. Loop onset per response: first word of the first 8-gram that occurs >= 3 times, mapped to a token index.
3. Teacher-forced pass over prompt + response; residual stream after every decoder layer (hidden_states[l+1]).
   Per response: mean over in-loop tokens minus mean over pre-onset response tokens. u_l = normalized average.
4. Separation per layer = mean / std of the per-response difference projected on u_l; top-2 layers in [4, 22].

Outputs (results/direction/): u.npz (U: n_layers x hidden), summary.json, contrast_responses.jsonl.
"""
import argparse
import re
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import metrics as M  # noqa: E402
import runner as R  # noqa: E402

D = R.SPEC["direction"]


def onset_token(tok, ids, text, onset_word):
    """Map a word index (whitespace tokens) to the first response token whose decoded prefix covers it."""
    starts = [m.start() for m in re.finditer(r"\S+", text)]
    char_start = starts[onset_word]
    lo, hi = 0, len(ids) - 1
    while lo < hi:  # smallest j with len(decode(ids[:j+1])) > char_start
        mid = (lo + hi) // 2
        if len(tok.decode(ids[:mid + 1], skip_special_tokens=True)) > char_start:
            hi = mid
        else:
            lo = mid + 1
    return lo


def generate_with_ids(ctx, items):
    import torch
    tok, model = ctx.tok, ctx.model
    stop = set(model.generation_config.eos_token_id if isinstance(model.generation_config.eos_token_id, list)
               else [model.generation_config.eos_token_id]) | {tok.pad_token_id}
    out = []
    bs = R.SPEC["batch_size"]
    for i in range(0, len(items), bs):
        batch = items[i:i + bs]
        prompts = [C.chat_prompt(tok, it["text"], template_kwargs=ctx.mc.get("template_kwargs")) for it in batch]
        enc = tok(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
        with torch.no_grad():
            gen = model.generate(**enc, max_new_tokens=R.SPEC["max_new_tokens"], pad_token_id=tok.pad_token_id,
                                 **{**R.decoding_kwargs("greedy"), "temperature": None, "top_p": None, "top_k": None})
        new = gen[:, enc["input_ids"].shape[1]:].tolist()
        for it, p, ids in zip(batch, prompts, new):
            cut = next((j for j, t in enumerate(ids) if t in stop), len(ids))
            ids = ids[:cut]
            out.append(dict(item=it, prompt_text=p, ids=ids, text=tok.decode(ids, skip_special_tokens=True)))
        print(f"  generated {min(i + bs, len(items))}/{len(items)}")
    return out


def activations(ctx, prompt_text, ids):
    """(n_layers, n_response_tokens, hidden) residual stream after each decoder layer."""
    import torch
    p_ids = ctx.tok(prompt_text, return_tensors="pt", add_special_tokens=False)["input_ids"][0].tolist()
    x = torch.tensor([p_ids + ids], device=ctx.model.device)
    with torch.no_grad():
        hs = ctx.model(x, output_hidden_states=True).hidden_states
    P, n_layers = len(p_ids), len(hs) - 1
    return np.stack([hs[l + 1][0, P:P + len(ids)].float().cpu().numpy() for l in range(n_layers)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    args = ap.parse_args()
    out_dir = C.RESULTS / ("direction_mock" if args.mock else "direction")
    out_dir.mkdir(parents=True, exist_ok=True)
    items = C.load_jsonl(C.DATA / "contrast_sv.jsonl")
    ctx = R.Ctx(mock=args.mock).load()
    t0 = time.time()

    if args.mock:
        rng = np.random.default_rng(0)
        n_layers, hidden = 24, 896
        shift = rng.standard_normal(hidden)
        gens = R._mock_texts(ctx, items, "contrast_sv", "greedy", 0, None)
        resp = [dict(item=it, text=g["response"], ids=list(range(len(M.words(g["response"])))))
                for it, g in zip(items, gens)]
    else:
        resp = generate_with_ids(ctx, items)
    t_gen = time.time() - t0

    diffs, rows = [], []
    for r in resp:
        ow = M.loop_onset_word(r["text"])
        row = dict(id=r["item"]["id"], prompt=r["item"]["text"], response=r["text"], n_tokens=len(r["ids"]),
                   loop=ow is not None, onset_word=ow, onset_token=None, used=False)
        if ow is not None and r["ids"]:
            ot = ow if args.mock else onset_token(ctx.tok, r["ids"], r["text"], ow)
            row["onset_token"] = ot
            if ot >= D["min_pre_onset_tokens"] and len(r["ids"]) - ot >= D["min_in_loop_tokens"]:
                if args.mock:
                    A = rng.standard_normal((n_layers, len(r["ids"]), hidden))
                    A[:, ot:] += 0.5 * shift
                else:
                    A = activations(ctx, r["prompt_text"], r["ids"])
                diffs.append(A[:, ot:].mean(1) - A[:, :ot].mean(1))   # (n_layers, hidden)
                row["used"] = True
        rows.append(row)
    C.write_jsonl(out_dir / "contrast_responses.jsonl", rows)

    n_loop, n_used = sum(r["loop"] for r in rows), len(diffs)
    print(f"Responses with a loop: {n_loop}/150; usable for the direction: {n_used}")
    if n_used < D["min_responses_with_onset"]:
        C.write_json(out_dir / "summary.json", dict(error="too few usable responses", n_loop=n_loop, n_used=n_used))
        sys.exit(f"STOP: fewer than {D['min_responses_with_onset']} usable responses. Report to the main thread.")

    Dm = np.stack(diffs)                         # (n_resp, n_layers, hidden)
    mean = Dm.mean(0)
    U = mean / np.linalg.norm(mean, axis=1, keepdims=True)
    proj = np.einsum("rlh,lh->rl", Dm, U)        # per-response difference projected on u_l
    sep = proj.mean(0) / proj.std(0, ddof=1)
    lo, hi = D["layer_choice_range"]
    cand = [l for l in range(lo, hi + 1)]
    top2 = sorted(sorted(cand, key=lambda l: -sep[l])[:2])
    np.savez(out_dir / "u.npz", U=U.astype(np.float32), raw_norm=np.linalg.norm(mean, axis=1))
    summary = dict(time=C.now(), model=ctx.name, revision=ctx.revision, n_prompts=len(items), n_loop=n_loop,
                   n_used=n_used, separation=[round(float(s), 3) for s in sep], top2=top2,
                   diff_norm=[round(float(x), 3) for x in np.linalg.norm(mean, axis=1)],
                   median_onset_token=float(np.median([r["onset_token"] for r in rows if r["used"]])),
                   seconds_generation=round(t_gen, 1), seconds_total=round(time.time() - t0, 1), spec=D)
    C.write_json(out_dir / "summary.json", summary)
    if not args.mock:
        C.log_feedback("Step 4: loop direction (contrast_sv greedy generation + teacher-forced activations)",
                       ctx.name, n_prompts=len(items), condition="C0", note=f"revision {ctx.revision}")
    print("Separation by layer:", " ".join(f"L{l}:{s:.2f}" for l, s in enumerate(sep)))
    print(f"Top-2 layers in [{lo},{hi}]: {top2}.  Wrote {out_dir.relative_to(C.ROOT)}/u.npz and summary.json "
          f"({summary['seconds_total']:.0f}s)")


if __name__ == "__main__":
    main()
