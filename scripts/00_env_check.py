"""Step 0: check the Python environment.  Usage:  python scripts/00_env_check.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

info = C.env_info()
print(json.dumps(info, indent=2))
problems = []
if tuple(int(x) for x in info["python"].split(".")[:2]) < (3, 10):
    problems.append("Python >= 3.10 recommended")
for mod in ("torch", "transformers", "huggingface_hub", "lingua", "numpy", "scipy"):
    if info.get(mod) is None:
        problems.append(f"missing package: {mod} (run: pip install -r requirements.txt)")
if info.get("transformers"):
    major, minor = (int(x) for x in info["transformers"].split(".")[:2])
    if (major, minor) < (4, 51):
        problems.append("transformers >= 4.51 needed for Qwen3")
if info.get("torch") and not info.get("mps_available"):
    problems.append("MPS not available: will run on CPU (slower, still fine)")
if info.get("lingua"):
    print("lingua test:", C.detect_lang("Det här är en mening på svenska om vädret i Stockholm."),
          C.detect_lang("This is an English sentence about the weather."))
print("\nOK, ready." if not problems else "\nProblems:\n- " + "\n- ".join(problems))
