"""Shared helpers: data I/O, model loading, batched generation, language ID, logging."""
import datetime as _dt
import json
import math
import platform
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
CONFIGS = ROOT / "configs"

# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def write_jsonl(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def now():
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def log_feedback(purpose, model, n_prompts, n_passes=1, condition=None, note=None):
    """Append one entry to the feedback budget log (every evaluation pass used for a decision)."""
    entry = dict(time=now(), purpose=purpose, model=model, condition=condition,
                 n_prompts=n_prompts, n_passes=n_passes, note=note)
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "feedback_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def env_info():
    info = dict(python=sys.version.split()[0], platform=platform.platform(), machine=platform.machine())
    for mod in ("torch", "transformers", "huggingface_hub", "lingua", "numpy", "scipy"):
        try:
            m = __import__(mod)
            info[mod] = getattr(m, "__version__", "installed")
        except ImportError:
            info[mod] = None
    try:
        import torch
        info["mps_available"] = torch.backends.mps.is_available()
        info["cuda_available"] = torch.cuda.is_available()
    except ImportError:
        pass
    return info


# ---------------------------------------------------------------------------
# Language identification (pre-registered: lingua restricted to sv/en/nb/nn/da/de;
# responses under 20 characters count as failures)
# ---------------------------------------------------------------------------

MIN_CHARS = 20
_DETECTOR = None


def _detector():
    global _DETECTOR
    if _DETECTOR is None:
        from lingua import Language, LanguageDetectorBuilder
        langs = [Language.SWEDISH, Language.ENGLISH, Language.BOKMAL, Language.NYNORSK,
                 Language.DANISH, Language.GERMAN]
        _DETECTOR = LanguageDetectorBuilder.from_languages(*langs).with_preloaded_language_models().build()
    return _DETECTOR


_LANG_CODE = {"SWEDISH": "sv", "ENGLISH": "en", "BOKMAL": "nb", "NYNORSK": "nn", "DANISH": "da", "GERMAN": "de"}


def detect_lang(text):
    """Return 'sv','en','nb','nn','da','de', 'short' (<20 chars) or 'unknown'."""
    t = (text or "").strip()
    if len(t) < MIN_CHARS:
        return "short"
    lang = _detector().detect_language_of(t)
    if lang is None:
        return "unknown"
    return _LANG_CODE.get(lang.name, "unknown")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


def load_model_configs():
    return json.loads((CONFIGS / "models.json").read_text(encoding="utf-8"))


def model_config(name):
    for c in load_model_configs()["candidates"]:
        if c["name"] == name:
            return c
    raise KeyError(name)


def pinned_revision(name):
    """Commit sha pinned in pilot 1 (results/model_revisions.json)."""
    path = RESULTS / "model_revisions.json"
    if not path.exists():
        raise FileNotFoundError("results/model_revisions.json missing: run scripts/02_pilot.py first")
    return json.loads(path.read_text(encoding="utf-8"))[name]["revision"]


def resolve_revision(repo_id, revision=None):
    """Return the exact commit sha for a model repo (pin it so results are reproducible)."""
    if revision and re.fullmatch(r"[0-9a-f]{40}", revision):
        return revision
    from huggingface_hub import HfApi
    return HfApi().model_info(repo_id, revision=revision).sha


def get_device():
    import torch
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def load_model(repo_id, revision, device, dtype="float32"):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(repo_id, revision=revision)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(repo_id, revision=revision,
                                                 dtype=getattr(torch, dtype))
    model.to(device).eval()
    return tok, model


def chat_prompt(tok, user_text, system=None, template_kwargs=None):
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user_text}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **(template_kwargs or {}))


_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.S)


def clean_response(text):
    return _THINK_RE.sub("", text).strip()


def generate(tok, model, prompts, max_new_tokens=256, batch_size=8, do_sample=False,
             temperature=None, top_p=None, top_k=None, min_p=None, repetition_penalty=1.0,
             seed=None, progress=True):
    """Batched generation. Greedy with repetition_penalty=1.0 by default. Every decoding setting is
    passed explicitly, so the model repo's own generation_config defaults never apply silently."""
    import torch
    from tqdm import tqdm
    outs = []
    gen_kwargs = dict(max_new_tokens=max_new_tokens, do_sample=do_sample,
                      repetition_penalty=repetition_penalty, pad_token_id=tok.pad_token_id)
    if do_sample:
        gen_kwargs.update(temperature=temperature, top_p=1.0 if top_p is None else top_p,
                          top_k=0 if top_k is None else top_k)
        if min_p is not None:
            gen_kwargs["min_p"] = min_p
    else:
        gen_kwargs.update(temperature=None, top_p=None, top_k=None)
    if seed is not None:
        torch.manual_seed(seed)
    rng = range(0, len(prompts), batch_size)
    for i in (tqdm(rng, desc="generate", leave=False) if progress else rng):
        batch = prompts[i:i + batch_size]
        enc = tok(batch, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
        with torch.no_grad():
            out = model.generate(**enc, **gen_kwargs)
        new = out[:, enc["input_ids"].shape[1]:]
        for row in new:
            n_tok = int((row != tok.pad_token_id).sum())
            outs.append(dict(response=clean_response(tok.decode(row, skip_special_tokens=True)),
                             n_new_tokens=n_tok, hit_limit=n_tok >= max_new_tokens))
    return outs


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))
