"""Step 2: build the synthetic data sets in data/.

Usage:  python scripts/01_make_data.py

Deterministic (fixed seed). Writes JSONL files, data/MANIFEST.json (counts + sha256) and
data/SPOTCHECK.md (random sv/en pairs for a human to read).

Splits (see docs/02_hypothesis.md, section 2.6):
  open prompts : dev 80, test 120, contrast 150   (parallel sv/en)
  math         : dev 60, test 100                  (parallel sv/en, integer answers)
  ref          : test 50                           (parallel sv/en paragraphs)

Open prompts are split by *topic*: a topic used in dev never appears in test or contrast,
so dev-set selection cannot leak into the test set through shared topics.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_sources import (MATH_SUFFIX, MATH_TEMPLATES, OPEN_STANDALONE, OPEN_TEMPLATES,  # noqa: E402
                          OPEN_TOPICS, REF_PARAGRAPHS)

SEED = 20261119
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# number of topics / stand-alone prompts per split; 4 templates per topic
TEMPLATES_PER_TOPIC = 4
OPEN_PLAN = {            # (n_topics, n_standalone) -> 4*n_topics + n_standalone prompts
    "dev": (15, 20),     # 80
    "test": (22, 32),    # 120
    "contrast": (35, 10),  # 150
}
MATH_PLAN = {"dev": 60, "test": 100}


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_open(rng):
    topic_idx = list(range(len(OPEN_TOPICS)))
    stand_idx = list(range(len(OPEN_STANDALONE)))
    rng.shuffle(topic_idx)
    rng.shuffle(stand_idx)
    need_t = sum(t for t, _ in OPEN_PLAN.values())
    need_s = sum(s for _, s in OPEN_PLAN.values())
    assert need_t <= len(topic_idx) and need_s <= len(stand_idx), "not enough source material"

    out = {}
    ti, si = 0, 0
    for split, (n_t, n_s) in OPEN_PLAN.items():
        items = []
        for t in topic_idx[ti:ti + n_t]:
            for k in sorted(rng.sample(range(len(OPEN_TEMPLATES)), TEMPLATES_PER_TOPIC)):
                sv_t, en_t = OPEN_TEMPLATES[k]
                sv_x, en_x = OPEN_TOPICS[t]
                items.append(dict(source="topic", cluster=f"t{t:02d}", template=f"k{k}",
                                  sv=sv_t.format(x=sv_x), en=en_t.format(x=en_x)))
        for s in stand_idx[si:si + n_s]:
            sv, en = OPEN_STANDALONE[s]
            items.append(dict(source="standalone", cluster=f"s{s:02d}", template=None, sv=sv, en=en))
        ti += n_t
        si += n_s
        rng.shuffle(items)
        out[split] = items
    return out


def build_math(rng):
    total = sum(MATH_PLAN.values())
    seen, items = set(), []
    i = 0
    while len(items) < total:
        tid, sv_t, en_t, sampler = MATH_TEMPLATES[i % len(MATH_TEMPLATES)]
        fields, answer = sampler(rng)
        sv = f"{sv_t.format(**fields)} {MATH_SUFFIX[0]}"
        en = f"{en_t.format(**fields)} {MATH_SUFFIX[1]}"
        i += 1
        if sv in seen:
            continue
        seen.add(sv)
        assert isinstance(answer, int) and answer >= 0, (tid, fields, answer)
        items.append(dict(template=tid, sv=sv, en=en, answer=answer))
    rng.shuffle(items)
    out, start = {}, 0
    for split, n in MATH_PLAN.items():
        out[split] = items[start:start + n]
        start += n
    return out


def main():
    rng = random.Random(SEED)
    DATA.mkdir(exist_ok=True)
    files = {}

    # --- open prompts + contrast ---------------------------------------------------
    open_sets = build_open(rng)
    for split, items in open_sets.items():
        for lang in ("sv", "en"):
            rows = [dict(id=f"open_{split}_{j:03d}", lang=lang, split=split, text=it[lang],
                         source=it["source"], cluster=it["cluster"], template=it["template"])
                    for j, it in enumerate(items)]
            name = f"contrast_{lang}.jsonl" if split == "contrast" else f"{lang}_open_{split}.jsonl"
            write_jsonl(DATA / name, rows)
            files[name] = len(rows)

    # --- math --------------------------------------------------------------------
    math_sets = build_math(rng)
    for split, items in math_sets.items():
        for lang in ("sv", "en"):
            rows = [dict(id=f"math_{split}_{j:03d}", lang=lang, split=split, text=it[lang],
                         answer=it["answer"], template=it["template"])
                    for j, it in enumerate(items)]
            name = f"{lang}_math_{split}.jsonl"
            write_jsonl(DATA / name, rows)
            files[name] = len(rows)

    # --- reference paragraphs (test only) -----------------------------------------
    for li, lang in enumerate(("sv", "en")):
        rows = [dict(id=f"ref_test_{j:03d}", lang=lang, split="test", text=p[li])
                for j, p in enumerate(REF_PARAGRAPHS)]
        name = f"{lang}_ref_test.jsonl"
        write_jsonl(DATA / name, rows)
        files[name] = len(rows)

    # --- checks ------------------------------------------------------------------
    clusters = {s: {it["cluster"] for it in items} for s, items in open_sets.items()}
    assert not (clusters["dev"] & clusters["test"]), "dev/test share a topic"
    assert not (clusters["dev"] & clusters["contrast"]), "dev/contrast share a topic"
    assert not (clusters["test"] & clusters["contrast"]), "test/contrast share a topic"
    for lang in ("sv", "en"):
        texts = []
        for name in files:
            if name.startswith(f"{lang}_") or name == f"contrast_{lang}.jsonl":
                texts += [json.loads(l)["text"] for l in open(DATA / name, encoding="utf-8")]
        assert len(texts) == len(set(texts)), f"duplicate {lang} texts across sets"
    expected = {"sv_open_dev.jsonl": 80, "sv_open_test.jsonl": 120, "contrast_sv.jsonl": 150,
                "sv_math_dev.jsonl": 60, "sv_math_test.jsonl": 100, "sv_ref_test.jsonl": 50}
    for name, n in expected.items():
        assert files[name] == n, (name, files[name], n)
        assert files[name.replace("sv", "en")] == n

    # --- manifest + spot-check sheet ---------------------------------------------
    manifest = dict(seed=SEED, generator="scripts/01_make_data.py",
                    source_material="scripts/data_sources.py (written by Claude, spot-checked by the author)",
                    files={n: dict(rows=c, sha256=sha256(DATA / n)) for n, c in sorted(files.items())})
    (DATA / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    spot = random.Random(SEED + 1)
    lines = ["# Spot-check sheet", "",
             "Random sv/en pairs from each set (seed fixed). Check: natural Swedish, faithful English, "
             "correct math answers. Note problems at the bottom.", ""]
    for stem, label in [("open_dev", "Open prompts (dev)"), ("open_test", "Open prompts (test)"),
                        ("contrast", "Contrast prompts"), ("math_dev", "Math (dev)"),
                        ("math_test", "Math (test)"), ("ref_test", "Reference paragraphs")]:
        if stem == "contrast":
            sv_rows = [json.loads(l) for l in open(DATA / "contrast_sv.jsonl", encoding="utf-8")]
            en_rows = [json.loads(l) for l in open(DATA / "contrast_en.jsonl", encoding="utf-8")]
        else:
            sv_rows = [json.loads(l) for l in open(DATA / f"sv_{stem}.jsonl", encoding="utf-8")]
            en_rows = [json.loads(l) for l in open(DATA / f"en_{stem}.jsonl", encoding="utf-8")]
        lines += [f"## {label}", ""]
        for j in sorted(spot.sample(range(len(sv_rows)), min(5, len(sv_rows)))):
            a = f"  (answer: {sv_rows[j]['answer']})" if "answer" in sv_rows[j] else ""
            lines += [f"- **{sv_rows[j]['id']}**{a}", f"  - sv: {sv_rows[j]['text']}",
                      f"  - en: {en_rows[j]['text']}"]
        lines.append("")
    lines += ["## Problems found", "", "- (none yet)", ""]
    (DATA / "SPOTCHECK.md").write_text("\n".join(lines), encoding="utf-8")

    print("Wrote data sets to data/:")
    for n, c in sorted(files.items()):
        print(f"  {n:24s} {c:4d} rows")
    print("All split/disjointness checks passed. Read data/SPOTCHECK.md next.")


if __name__ == "__main__":
    main()
