import hashlib
import json

def normalize_weights(w):
    total = sum(w.values())
    if total == 0:
        raise ValueError("Weights cannot be zero")
    return {k: v/total for k, v in w.items()}

def scenario_key_from_weights(w):
    w = normalize_weights(w)
    s = json.dumps(w, sort_keys=True)
    return hashlib.md5(s.encode()).hexdigest()[:8]