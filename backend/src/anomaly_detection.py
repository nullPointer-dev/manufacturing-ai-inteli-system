import pandas as pd
from sklearn.ensemble import IsolationForest
from data_pipeline import build_pipeline


def detect_anomalies(df, contamination=0.1, random_state=42):
    df = df.copy()

    numeric_cols = df.select_dtypes(include=['number']).columns
    X = df[numeric_cols]

    iso = IsolationForest(contamination=contamination, random_state=random_state)
    iso.fit(X)

    df["anomaly_score"] = -iso.decision_function(X)
    df["anomaly_flag"] = (iso.predict(X) == -1).astype(int)

    df["risk_level"] = pd.cut(
        df["anomaly_score"],
        bins=[-float("inf"), 0.05, 0.10, float("inf")],
        labels=["Low", "Medium", "High"]
    )

    return df


def main():
    df = build_pipeline()
    anomalies = detect_anomalies(df)

    print(f"\nTotal anomalies detected: {len(anomalies)}")
    print("\nTop anomalous batches:")
    print(
        anomalies
        .sort_values('anomaly_score', ascending=False)
        .head(10)[["Batch_ID", "anomaly_score", "risk_level"]]
    )


if __name__ == "__main__":
    main()