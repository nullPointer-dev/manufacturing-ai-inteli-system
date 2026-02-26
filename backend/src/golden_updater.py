import json
from pathlib import Path
from datetime import datetime

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
REG_FILE = MODEL_DIR / "golden_registry.json"
HISTORY_FILE = MODEL_DIR / "golden_history.json"

IMPROVEMENT_THRESHOLD = 0.01  # 1%


# =========================================================
# SAFE JSON LOAD
# =========================================================
def _safe_load(path, default):
    if not path.exists():
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default


# =========================================================
# RELIABILITY GUARD
# =========================================================
def reliability_guard(best_row, prev_energy=None):

    if best_row is None:
        return False

    energy = float(best_row.get("Energy", 0))

    if prev_energy is not None:
        if abs(energy - prev_energy) > 0.15 * max(prev_energy, 1):
            return False

    if best_row.get("anomaly_flag", 0) == 1:
        return False

    return True


# =========================================================
# INTERNAL: GET PREVIOUS ENTRY
# =========================================================
def _get_previous(registry, mode, cluster_id, scenario_key):

    mode_registry = registry.get(mode, {})

    # ---------- CUSTOM MODE ----------
    if mode == "custom":
        if scenario_key is None:
            return None

        scenario_registry = mode_registry.get(scenario_key, {})
        return scenario_registry.get(f"cluster_{cluster_id}")

    # ---------- PRESET MODES ----------
    return mode_registry.get(f"cluster_{cluster_id}")


# =========================================================
# INTERNAL: WRITE ENTRY
# =========================================================
def _write_registry(registry, mode, cluster_id, entry, scenario_key):

    if mode not in registry:
        registry[mode] = {}

    # ---------- CUSTOM MODE ----------
    if mode == "custom":
        if scenario_key is None:
            raise ValueError("Custom mode requires scenario_key")

        if scenario_key not in registry[mode]:
            registry[mode][scenario_key] = {}

        registry[mode][scenario_key][f"cluster_{cluster_id}"] = entry
        return entry

    # ---------- PRESET MODES ----------
    registry[mode][f"cluster_{cluster_id}"] = entry
    return entry


# =========================================================
# MAIN UPDATE FUNCTION
# =========================================================
def check_and_update_golden(
    best_row,
    mode,
    cluster_id,
    scenario_key=None,
    force=False
):

    if best_row is None:
        return False

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    score = float(best_row.get("Score", 0))

    registry = _safe_load(REG_FILE, {})

    prev = _get_previous(registry, mode, cluster_id, scenario_key)

    prev_score = prev.get("score") if prev else None
    prev_energy = prev.get("energy") if prev else None

    should_update = False
    update_type = "INITIAL"

    if force:
        should_update = True
        update_type = "FORCED"

    elif prev_score is None:
        should_update = True
        update_type = "INITIAL"

    elif score > prev_score * (1 + IMPROVEMENT_THRESHOLD):
        should_update = True
        update_type = "IMPROVED"

    if not should_update:
        return False

    if not reliability_guard(best_row, prev_energy):
        return False

    # Build entry
    entry = {
        "score": score,
        "quality": float(best_row.get("Quality", 0)),
        "yield": float(best_row.get("Yield", 0)),
        "performance": float(best_row.get("Performance", 0)),
        "energy": float(best_row.get("Energy", 0)),
        "co2": float(best_row.get("CO2", 0)),
    }

    # Write registry
    saved_entry = _write_registry(
        registry,
        mode,
        cluster_id,
        entry,
        scenario_key
    )

    with open(REG_FILE, "w") as f:
        json.dump(registry, f, indent=2)

    # -----------------------------
    # HISTORY LOG
    # -----------------------------
    history = _safe_load(HISTORY_FILE, [])

    history_entry = {
        "time": datetime.now().isoformat(),
        "mode": mode,
        "scenario_key": scenario_key,
        "cluster": int(cluster_id),
        "type": update_type,
        "metrics": saved_entry
    }

    history.append(history_entry)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

    return True


# =========================================================
# CHECK ONLY (NO UPDATE)
# =========================================================
def check_if_better(
    best_row,
    mode,
    cluster_id,
    scenario_key=None
):

    if best_row is None:
        return False

    score = float(best_row.get("Score", 0))

    registry = _safe_load(REG_FILE, {})

    prev = _get_previous(registry, mode, cluster_id, scenario_key)

    prev_score = prev.get("score") if prev else None

    if prev_score is None:
        return True

    if score > prev_score * (1 + IMPROVEMENT_THRESHOLD):
        return True

    return False