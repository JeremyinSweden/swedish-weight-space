"""Shared generation + scoring for Steps 4-6, with a numpy-only mock mode for pipeline tests."""
import json
import random
import time

import common as C
import metrics as M

SPEC = json.loads((C.CONFIGS / "step4_6.json").read_text(encoding="utf-8"))


class Ctx:
    """Holds the model (or mock state). mock_strength simulates an edit in mock mode (0 = none)."""

    def __init__(self, mock=False):
        self.mock = mock
        self.mock_strength = 0.0
        self.tok = self.model = None
        self.name = SPEC["model"]
        self.revision = "mock" if mock else C.pinned_revision(self.name)
        self.mc = C.model_config(self.name)

    def load(self):
        if not self.mock:
            dev = C.get_device()
            print(f"Loading {self.mc['repo_id']} @ {self.revision[:10]} on {dev}")
            self.tok, self.model = C.load_model(self.mc["repo_id"], self.revision, dev)
        return self


def decoding_kwargs(name):
    d = dict(SPEC["greedy"] if name == "greedy" else SPEC[name])
    return {k: v for k, v in d.items() if not k.startswith("_")}


def _mock_texts(ctx, items, set_name, decoding, seed, system):
    rng = random.Random(f"{seed}-{set_name}-{decoding}-{system}-{ctx.mock_strength}")
    base = {"sv_open": 0.9, "en_open": 0.2, "sv_math": 0.03, "en_math": 0.0, "contrast_sv": 0.9}[set_name]
    p = base * (1 - ctx.mock_strength) * (0.5 if decoding != "greedy" else 1.0) * (0.8 if system else 1.0)
    out = []
    for it in items:
        if rng.random() < p:
            txt = "Det här är en bra början. " + "Detta är en del av en ordning som är en ordning av ord. " * 25
            out.append(dict(response=txt, n_new_tokens=SPEC["max_new_tokens"], hit_limit=True))
        else:
            ans = it.get("answer", 0) if rng.random() < 0.5 else rng.randint(0, 99)
            txt = f"Här är ett kort och tydligt svar på frågan, med några olika ord. Svaret blir {ans}"
            n = rng.choice([12, 40, 120, 200])
            out.append(dict(response=txt, n_new_tokens=n, hit_limit=False))
    return out


def generate_rows(ctx, items, set_name, decoding="greedy", seed=0, system=None, progress=True):
    t0 = time.time()
    if ctx.mock:
        gens = _mock_texts(ctx, items, set_name, decoding, seed, system)
    else:
        texts = [C.chat_prompt(ctx.tok, it["text"], system=system,
                               template_kwargs=ctx.mc.get("template_kwargs")) for it in items]
        gens = C.generate(ctx.tok, ctx.model, texts, max_new_tokens=SPEC["max_new_tokens"],
                          batch_size=SPEC["batch_size"], seed=seed, progress=progress, **decoding_kwargs(decoding))
    rows = []
    for it, g in zip(items, gens):
        r = dict(id=it["id"], prompt=it["text"], response=g["response"], n_new_tokens=g["n_new_tokens"],
                 hit_limit=g["hit_limit"], loop=M.is_loop(g["response"]), short=g["n_new_tokens"] < 30,
                 distinct2=distinct2(g["response"]))
        if "cluster" in it:
            r["cluster"] = it["cluster"]
        if "answer" in it:
            r.update(answer=it["answer"], extracted=M.extract_last_number(g["response"]),
                     correct=M.math_correct(g["response"], it["answer"]))
        rows.append(r)
    return rows, time.time() - t0


def distinct2(text):
    w = M.words(text)
    if len(w) < 2:
        return 1.0
    grams = list(zip(w, w[1:]))
    return len(set(grams)) / len(grams)


def rate(rows, key):
    return sum(bool(r[key]) for r in rows) / len(rows) if rows else float("nan")


def early_stop(rows_sv, rows_en, base_sv, base_en):
    """Deviation 5 item 3. Returns dict with the three checks and overall pass."""
    d_sv = rate(rows_sv, "short") - rate(base_sv, "short")
    checks = dict(short_rise_sv=d_sv, ok_sv=d_sv <= 0.10)
    if rows_en is not None and base_en is not None:
        d_en = rate(rows_en, "short") - rate(base_en, "short")
        m, m0 = M.median([r["n_new_tokens"] for r in rows_en]), M.median([r["n_new_tokens"] for r in base_en])
        ratio = m / m0 if m0 else float("nan")
        checks.update(short_rise_en=d_en, ok_en=d_en <= 0.10, en_median_ratio=ratio,
                      ok_en_median=abs(ratio - 1) <= 0.30)
    checks["passes"] = all(v for k, v in checks.items() if k.startswith("ok"))
    return checks


def perplexity(ctx, items):
    """Teacher-forced perplexity on plain text (no chat template). Mock: a fixed fake value."""
    if ctx.mock:
        return 20.0 * (1 + 0.02 * ctx.mock_strength)
    import math
    import torch
    nll, n = 0.0, 0
    for it in items:
        ids = ctx.tok(it["text"], return_tensors="pt", add_special_tokens=False)["input_ids"].to(ctx.model.device)
        with torch.no_grad():
            logits = ctx.model(ids).logits.float()
        lp = torch.log_softmax(logits[0, :-1], dim=-1)
        tgt = ids[0, 1:]
        nll -= float(lp.gather(1, tgt.unsqueeze(1)).sum())
        n += int(tgt.numel())
    return math.exp(nll / n)
