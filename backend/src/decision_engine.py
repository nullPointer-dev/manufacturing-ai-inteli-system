import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DECISION_FILE = BASE_DIR / "models" / "decision_memory.json"

def log_decision(mode, cluster_id, engine, weights, decision, reason, best_metrics):

    clean_weights = {k: float(v) for k, v in weights.items()}
    clean_metrics = {k: float(v) for k, v in best_metrics.items()}

    entry = {
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "cluster_id": int(cluster_id),
        "engine": engine,
        "weights": clean_weights,
        "decision": decision,
        "reason": reason,
        "best_metrics": clean_metrics
    }

    if DECISION_FILE.exists():
        try:
            with open(DECISION_FILE, "r") as f:
                history = json.load(f)
        except Exception:
            history = []
    else:
        history = []

    history.append(entry)

    DECISION_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(DECISION_FILE, "w") as f:
        json.dump(history, f, indent=2)