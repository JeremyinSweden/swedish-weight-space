# Test results (Step 6)

Frozen config: C3 = g6_L15-19_k1024_a1 (layers [15, 19], k=1024, alpha=1.0); C2 alpha_s=1.0.

| Condition | Set | n | Loop | 95% CI | Hit 512 | Short <30 | Median tokens | Distinct-2 | Math acc |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|
| C0 | sv_open | 120 | 90% | 83-94% | 78% | 1% | 512 | 0.25 | - |
| C0 | en_open | 120 | 14% | 9-22% | 5% | 2% | 252 | 0.80 | - |
| C0 | sv_math | 100 | 4% | 2-10% | 2% | 63% | 26 | 0.92 | 26% |
| C0 | en_math | 100 | 0% | 0-4% | 0% | 48% | 36 | 0.92 | 73% |
| C3 | sv_open | 120 | 94% | 88-97% | 76% | 0% | 512 | 0.24 | - |
| C3 | en_open | 120 | 14% | 9-22% | 6% | 2% | 274 | 0.80 | - |
| C3 | sv_math | 100 | 2% | 1-7% | 2% | 66% | 22 | 0.95 | 28% |
| C3 | en_math | 100 | 0% | 0-4% | 0% | 47% | 36 | 0.91 | 73% |
| C5s0 | sv_open | 120 | 90% | 83-94% | 78% | 2% | 512 | 0.26 | - |
| C5s0 | sv_math | 100 | 1% | 0-5% | 1% | 64% | 26 | 0.94 | 24% |
| C9 | sv_open | 120 | 22% | 15-30% | 38% | 0% | 450 | 0.81 | - |
| C9 | en_open | 120 | 0% | 0-3% | 2% | 2% | 272 | 0.96 | - |
| C9 | sv_math | 100 | 0% | 0-4% | 0% | 42% | 46 | 0.96 | 22% |
| C9 | en_math | 100 | 0% | 0-4% | 0% | 25% | 96 | 0.92 | 73% |
| C3def | sv_open | 120 | 24% | 17-33% | 27% | 1% | 404 | 0.82 | - |
| C3def | en_open | 120 | 0% | 0-3% | 3% | 2% | 279 | 0.96 | - |
| C3def | sv_math | 100 | 1% | 0-5% | 0% | 55% | 25 | 0.97 | 26% |
| C3def | en_math | 100 | 0% | 0-4% | 0% | 28% | 80 | 0.93 | 69% |
| C1 | sv_open | 120 | 79% | 71-85% | 60% | 2% | 512 | 0.31 | - |
| C1 | sv_math | 100 | 2% | 1-7% | 1% | 83% | 10 | 0.97 | 30% |
| C2 | sv_open | 120 | 56% | 47-64% | 42% | 14% | 167 | 0.47 | - |
| C2 | sv_math | 100 | 7% | 3-14% | 7% | 60% | 22 | 0.89 | 16% |
| C5s1 | sv_open | 120 | 93% | 87-97% | 80% | 2% | 512 | 0.24 | - |
| C5s1 | sv_math | 100 | 5% | 2-11% | 3% | 64% | 25 | 0.93 | 24% |
| C5s2 | sv_open | 120 | 91% | 84-95% | 78% | 1% | 512 | 0.26 | - |
| C5s2 | sv_math | 100 | 3% | 1-8% | 0% | 64% | 24 | 0.94 | 29% |

Perplexity (teacher-forced): C0: sv 91.01 / en 15.57, C3: sv 90.91 / en 15.56

## Paired comparisons (difference a - b; cluster bootstrap 95% CI; exact McNemar p)

| Metric | a | b | Set | Diff | 95% CI | McNemar p |
|---|---|---|---|---:|---|---:|
| sv_open_loop | C3 | C0 | sv_open | +4.2 pts | -2.2 to +10.5 | 0.302 |
| sv_open_loop | C3 | C5s0 | sv_open | +4.2 pts | -1.8 to +9.9 | 0.302 |
| sv_open_loop | C3 | C5s1 | sv_open | +0.8 pts | -4.9 to +6.1 | 1 |
| sv_open_loop | C3 | C5s2 | sv_open | +3.3 pts | -2.6 to +8.6 | 0.454 |
| sv_open_loop | C3 | C5mean | sv_open | +2.8 pts | -2.3 to +7.2 | - |
| sv_open_loop | C3 | C9 | sv_open | +72.5 pts | +63.4 to +81.1 | 2.91e-25 |
| sv_open_loop | C3def | C9 | sv_open | +2.5 pts | -8.5 to +12.9 | 0.755 |
| sv_open_loop | C9 | C0 | sv_open | -68.3 pts | -76.3 to -60.5 | 4.14e-25 |
| sv_open_loop | C1 | C0 | sv_open | -10.8 pts | -22.0 to +0.0 | 0.0351 |
| sv_open_loop | C2 | C0 | sv_open | -34.2 pts | -46.1 to -22.2 | 2.33e-09 |
| sv_open_loop | C3 | C1 | sv_open | +15.0 pts | +6.1 to +24.6 | 0.00143 |
| sv_open_loop | C3 | C2 | sv_open | +38.3 pts | +26.8 to +49.6 | 3.8e-11 |
| sv_open_loop | C5mean | C0 | sv_open | +1.4 pts | -2.8 to +6.0 | - |
| en_open_loop | C3 | C0 | en_open | +0.0 pts | -6.5 to +6.2 | 1 |
| en_open_loop | C3def | C9 | en_open | +0.0 pts | +0.0 to +0.0 | 1 |
| math_acc | C3 | C0 | sv_math | +2.0 pts | -2.0 to +7.0 | 0.688 |
| math_acc | C3 | C0 | en_math | +0.0 pts | +0.0 to +0.0 | 1 |
| math_acc | C3def | C9 | sv_math | +4.0 pts | -5.0 to +14.0 | 0.523 |
| math_acc | C3def | C9 | en_math | -4.0 pts | -11.0 to +2.0 | 0.388 |
| math_acc | C5mean | C0 | sv_math | -0.3 pts | -3.0 to +2.0 | - |
| math_acc | C1 | C0 | sv_math | +4.0 pts | -7.0 to +16.0 | 0.597 |
| math_acc | C2 | C0 | sv_math | -10.0 pts | -20.0 to -1.0 | 0.0639 |

## Early-stop checks

- C3 vs C0: pass {"short_rise_sv": -0.008, "ok_sv": true, "short_rise_en": 0.0, "ok_en": true, "en_median_ratio": 1.091, "ok_en_median": true, "passes": true}
- C3def vs C9: pass {"short_rise_sv": 0.008, "ok_sv": true, "short_rise_en": 0.0, "ok_en": true, "en_median_ratio": 1.024, "ok_en_median": true, "passes": true}
- C1 vs C0: pass {"short_rise_sv": 0.008, "ok_sv": true, "passes": true}
- C2 vs C0: FAIL {"short_rise_sv": 0.133, "ok_sv": false, "passes": false}
- C5s0 vs C0: pass {"short_rise_sv": 0.008, "ok_sv": true, "passes": true}

## Mechanical hypothesis checks (thresholds from Deviations 4-5; interpretation at checkpoint b)

```
{
  "H1prime": {
    "drop_vs_C0": 0.041666666666666664,
    "ci_vs_C5": [
      -0.022792022792022783,
      0.07222545219638242
    ],
    "mechanical": "challenged"
  },
  "H2prime": {
    "en_loop_diff": 0.0,
    "en_math_diff": 0.0,
    "ppl_rise": {
      "sv": -0.0011368023803424165,
      "en": -0.0005976252982776709
    },
    "early_stop": true,
    "mechanical": "supported"
  },
  "practical": {
    "C3_minus_C9": {
      "a": "C3",
      "b": "C9",
      "set": "sv_open",
      "metric": "loop",
      "diff": 0.725,
      "ci95": [
        0.6341260162601626,
        0.8108183183183183
      ],
      "mcnemar": {
        "b": 88,
        "c": 1,
        "p": 2.908056841006738e-25
      }
    },
    "C3def_minus_C9": {
      "a": "C3def",
      "b": "C9",
      "set": "sv_open",
      "metric": "loop",
      "diff": 0.025,
      "ci95": [
        -0.08511050634999175,
        0.12880892255892243
      ],
      "mcnemar": {
        "b": 22,
        "c": 19,
        "p": 0.755228657504631
      }
    },
    "C3_beats_C9": false,
    "C3def_beats_C9": false
  },
  "H3prime_partial": {
    "sv_math_diff": 0.02,
    "sv_ppl_change": -0.0011368023803424165,
    "note": "coherence ratings are done in the main thread (coherence_blind.jsonl)"
  }
}
```

Coherence items written: 160 (coherence_blind.jsonl). Finished conditions: ['C0', 'C1', 'C2', 'C3', 'C3def', 'C5s0', 'C5s1', 'C5s2', 'C9']. Missing cells: none.
