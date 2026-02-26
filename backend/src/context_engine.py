import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import joblib

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
CLUSTER_FILE = MODEL_DIR / "context_cluster.pkl"
SCALER_FILE = MODEL_DIR / "context_scaler.pkl"

# --------------------------------------------------
# Context features used for clustering
# --------------------------------------------------
CONTEXT_FEATURES = [
    "Batch_Size",
    "Machine_Speed",
    "Compression_Force",
    "avg_temperature",
    "avg_pressure"
]


# --------------------------------------------------
# Safe clustering utility
# --------------------------------------------------
def assign_context_clusters(df, n_clusters=3, persist=True):
    """
    Assign context clusters safely.

    Works even if:
    - some context columns missing
    - optimizer dataframe passed
    - very small dataset
    - model files missing
    """

    df = df.copy()

    # ------------------------------------------
    # Determine usable features
    # ------------------------------------------
    available = [c for c in CONTEXT_FEATURES if c in df.columns]

    # Not enough features → assign default cluster
    if len(available) < 2:
        df["context_cluster"] = 0
        return df, None

    X = df[available].fillna(df[available].median())

    # ------------------------------------------
    # If persisted model exists → reuse
    # ------------------------------------------
    if persist and CLUSTER_FILE.exists() and SCALER_FILE.exists():
        try:
            scaler = joblib.load(SCALER_FILE)
            kmeans = joblib.load(CLUSTER_FILE)

            X_scaled = scaler.transform(X)
            df["context_cluster"] = kmeans.predict(X_scaled)

            return df, kmeans

        except Exception:
            # corrupted model → rebuild
            pass

    # ------------------------------------------
    # Build new clustering model
    # ------------------------------------------
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # dynamic cluster count (prevents crash)
    safe_clusters = min(n_clusters, max(2, len(df) // 5))

    kmeans = KMeans(
        n_clusters=safe_clusters,
        random_state=42,
        n_init=10
    )

    df["context_cluster"] = kmeans.fit_predict(X_scaled)

    # ------------------------------------------
    # Persist model for consistency
    # ------------------------------------------
    if persist:
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(kmeans, CLUSTER_FILE)
        joblib.dump(scaler, SCALER_FILE)

    return df, kmeans