import numpy as np
import pandas as pd

def analyze_batch_against_golden(batch_row, golden_ranges, model = None, feature_cols = None):
    report = []

    for param, stats in golden_ranges.items():

        if param not in batch_row:
            continue

        current = batch_row[param]
        mean = stats["mean"]
        std  = stats["std"]

        if std == 0:
            std = abs(mean) * 0.05 + 1e-6

        drift = (current - mean) / std

        impact_estimate = 0.0

        if model is not None and feature_cols is not None and param in feature_cols:
            try:
                temp_row = batch_row.copy()

                # simulate correcting parameter toward golden mean
                temp_row[param] = mean

                X_current = pd.DataFrame([batch_row]).reindex(columns=feature_cols)
                X_corrected = pd.DataFrame([temp_row]).reindex(columns=feature_cols)

                X_current = X_current.apply(pd.to_numeric, errors="coerce").fillna(0.0)
                X_corrected = X_corrected.apply(pd.to_numeric, errors="coerce").fillna(0.0)

                pred_current = model.predict(X_current)[0]
                pred_corrected = model.predict(X_corrected)[0]

                # approximate quality delta
                impact_estimate = np.mean(pred_corrected - pred_current)

            except:
                impact_estimate = 0.0

        # severity classification
        if abs(drift) < 0.5:
            severity = "OK"
        elif abs(drift) < 1.5:
            severity = "Moderate"
        else:
            severity = "Critical"

        # Fallback impact estimate if model prediction is unavailable
        if abs(impact_estimate) < 1e-9:
            impact_estimate = -abs(drift) * 0.1

        # Determine if correcting toward golden mean is actually beneficial
        beneficial = impact_estimate >= 0

        # suggestion — only recommend action when correction improves quality
        if severity == "OK":
            suggestion = "Within optimal range"
        elif not beneficial:
            suggestion = "Monitor only — correction may reduce quality"
        elif current > mean:
            suggestion = f"Reduce toward {mean:.2f}"
        else:
            suggestion = f"Increase toward {mean:.2f}"

        report.append({
            "Parameter": param,
            "Current": current,
            "Golden Mean": mean,
            "Drift (σ)": drift,
            "Severity": severity,
            "Suggestion": suggestion,
            "Predicted Impact": float(impact_estimate),
            "Beneficial": beneficial
        })

    return pd.DataFrame(report)