"""Summarise the blind coherence ratings (Deviation 5, item 2).

Reads results/test/coherence_ratings_claude.txt, coherence_key.json and coherence_author20.md,
writes results/test/coherence_summary.json. No model needed.
Usage: python scripts/07_coherence_summary.py
"""
import json
import random
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results" / "test"
CONDS = ["C0", "C3", "C9", "C3def"]
N_BOOT, SEED = 5000, 0


def read_ratings(path):
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        p = line.split()
        if len(p) == 2 and p[0].startswith("R"):
            out[p[0]] = int(p[1])
    return out


def read_author(path):
    text = path.read_text(encoding="utf-8")
    ids = re.findall(r"^## (R\d+)", text, re.M)
    vals = re.findall(r"^Rating:\s*(\d?)", text, re.M)
    return {i: int(v) for i, v in zip(ids, vals) if v}


def paired_ci(a, b):
    d = [x - y for x, y in zip(a, b)]
    rng = random.Random(SEED)
    boots = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(N_BOOT))
    return [boots[int(0.025 * N_BOOT)], boots[int(0.975 * N_BOOT) - 1]]


def kappa(x, y):
    n = len(x)
    po = sum(a == b for a, b in zip(x, y)) / n
    cats = set(x) | set(y)
    pe = sum((x.count(c) / n) * (y.count(c) / n) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main():
    rat = read_ratings(T / "coherence_ratings_claude.txt")
    key = json.loads((T / "coherence_key.json").read_text(encoding="utf-8"))
    by = {c: {} for c in CONDS}
    for bid, k in key.items():
        by[k["condition"]][k["id"]] = (rat[bid], k)
    ids = sorted(by["C0"])
    out = dict(rater="Claude (Opus 5.5), blind", n_prompts=len(ids), scale="1-3", by_condition={}, paired={},
               rescue_strata={}, bootstrap=f"paired over the {len(ids)} prompts, {N_BOOT} resamples, seed {SEED}")
    for c in CONDS:
        rs = [by[c][i][0] for i in ids]
        lp = [by[c][i][0] for i in ids if by[c][i][1]["loop"]]
        nl = [by[c][i][0] for i in ids if not by[c][i][1]["loop"]]
        out["by_condition"][c] = dict(mean=round(statistics.mean(rs), 3), n_rated_1=rs.count(1), n_rated_2=rs.count(2),
                                      n_rated_3=rs.count(3),
                                      mean_looping=round(statistics.mean(lp), 3) if lp else None,
                                      mean_nonlooping=round(statistics.mean(nl), 3) if nl else None)
    for a, b in [("C3", "C0"), ("C9", "C0"), ("C3def", "C9"), ("C3def", "C0")]:
        xa = [by[a][i][0] for i in ids]
        xb = [by[b][i][0] for i in ids]
        out["paired"][f"{a}-{b}"] = dict(diff=round(statistics.mean(xa) - statistics.mean(xb), 3), ci95=paired_ci(xa, xb))
    for c in ["C3", "C9", "C3def"]:
        looped = [i for i in ids if by[c][i][1]["c0_loop"]]
        resc = [by[c][i][0] for i in looped if not by[c][i][1]["loop"]]
        out["rescue_strata"][c] = dict(c0_looped_prompts=len(looped), now_not_looping=len(resc),
                                       rated_3=resc.count(3),
                                       mean_rating_of_rescued=round(statistics.mean(resc), 3) if resc else None)
    auth = read_author(T / "coherence_author20.md")
    if auth:
        sub = sorted(auth)
        x, y = [auth[i] for i in sub], [rat[i] for i in sub]
        out["author_agreement"] = dict(
            items=len(sub), agree=sum(a == b for a, b in zip(x, y)),
            percent_agreement=round(sum(a == b for a, b in zip(x, y)) / len(sub), 3), cohens_kappa=round(kappa(x, y), 3),
            disagreements=[dict(blind_id=i, author=auth[i], claude=rat[i], condition=key[i]["condition"])
                           for i in sub if auth[i] != rat[i]],
            note="Both raters put almost every item at 1, so kappa is low by construction (prevalence effect); "
                 "percent agreement is the more informative number here.")
    (T / "coherence_summary.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out["by_condition"], indent=1))


if __name__ == "__main__":
    main()
