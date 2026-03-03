import json
import threading
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DECISION_FILE = BASE_DIR / "models" / "decision_memory.json"

# Protects the read-modify-write cycle against concurrent FastAPI request threads.
_decision_lock = threading.Lock()

# Maximum number of decision entries retained in memory (prevents unbounded growth).
_MAX_DECISION_ENTRIES = 10_000


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

    with _decision_lock:
        if DECISION_FILE.exists():
            try:
                with open(DECISION_FILE, "r") as f:
                    history = json.load(f)
            except Exception:
                history = []
        else:
            history = []

        history.append(entry)

        # Trim oldest entries once the cap is reached.
        if len(history) > _MAX_DECISION_ENTRIES:
            history = history[-_MAX_DECISION_ENTRIES:]

        DECISION_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(DECISION_FILE, "w") as f:
            json.dump(history, f, indent=2)