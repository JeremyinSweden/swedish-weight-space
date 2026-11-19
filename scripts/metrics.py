"""Behavioural metrics (pure Python + numpy, no model needed).

Loop definition (docs/02_hypothesis.md, Deviation 4): a response loops if some word-level 8-gram
(whitespace tokens, lowercased) occurs at least 3 times.
"""
import re
from collections import Counter

import numpy as np

LOOP_N = 8
LOOP_MIN_COUNT = 3


def words(text):
    return (text or "").lower().split()


def max_ngram_count(text, n=LOOP_N):
    w = words(text)
    if len(w) < n:
        return 0
    c = Counter(tuple(w[i:i + n]) for i in range(len(w) - n + 1))
    return max(c.values())


def is_loop(text, n=LOOP_N, min_count=LOOP_MIN_COUNT):
    return max_ngram_count(text, n) >= min_count


def loop_onset_word(text, n=LOOP_N, min_count=LOOP_MIN_COUNT):
    """Word index where the looping 8-gram first occurs (None if no loop). Used later to split
    pre-loop and in-loop tokens for the loop direction."""
    w = words(text)
    grams = [tuple(w[i:i + n]) for i in range(len(w) - n + 1)]
    c = Counter(grams)
    looping = {g for g, k in c.items() if k >= min_count}
    for i, g in enumerate(grams):
        if g in looping:
            return i
    return None


_NUM_RE = re.compile(r"-?\d+(?:[.,]\d+)?")


def extract_last_number(text):
    """Last number in the text, language independent ('3,5' and '3.5' both -> 3.5). None if absent."""
    nums = _NUM_RE.findall(text or "")
    if not nums:
        return None
    try:
        return float(nums[-1].replace(",", "."))
    except ValueError:
        return None


def math_correct(text, answer):
    x = extract_last_number(text)
    return x is not None and abs(x - float(answer)) < 1e-6


def median(xs):
    return float(np.median(xs)) if len(xs) else float("nan")


def cluster_bootstrap_diff(a, b, clusters, n_boot=2000, seed=0):
    """Paired difference mean(a) - mean(b) with a 95% CI, resampling clusters (topics).
    a, b: 0/1 arrays over the same items; clusters: cluster id per item."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d = a - b
    ids = sorted(set(clusters))
    idx = {c: np.array([i for i, x in enumerate(clusters) if x == c]) for c in ids}
    rng = np.random.default_rng(seed)
    stats = []
    for _ in range(n_boot):
        pick = rng.choice(len(ids), size=len(ids), replace=True)
        rows = np.concatenate([idx[ids[j]] for j in pick])
        stats.append(d[rows].mean())
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return float(d.mean()), float(lo), float(hi)
