import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
import joblib


class Rule:

    def load(self, path):
        data_path = path
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Dataset not found at {data_path}")

        df = pd.read_csv(data_path, encoding="latin-1")
        df.columns = (
            df.columns
            .str.strip()
            .str.replace("\x96", "-", regex=False)  # replace weird dash
            .str.replace("–", "-", regex=False)     # replace en dash
            .str.lower()
        )

        print("Cleaned columns:", df.columns.tolist())
        MEASURES = [
            "breast cancer screening",
            "colorectal cancer screening",
            "annual flu vaccine",
            "monitoring physical activity",
            "special needs plan (snp) care management",
            "care for older adults - medication review",
            "care for older adults - pain assessment",
            "osteoporosis management in women who had a fracture",
            "diabetes care - eye exam",
            "diabetes care - blood sugar controlled",
            "controlling blood pressure",
            "reducing the risk of falling",
            "improving bladder control",
            "medication reconciliation post-discharge",
            "plan all-cause readmissions",
            "statin therapy for patients with cardiovascular disease",
            "transitions of care",
            "follow-up after emergency department visit for people with multiple high-risk chronic conditions",
            "getting needed care",
            "getting appointments and care quickly",
            "customer service",
            "rating of health care quality",
            "rating of health plan",
            "care coordination",
            "complaints about the health plan",
            "members choosing to leave the plan",
            "health plan quality improvement",
            "plan makes timely decisions about appeals",
            "reviewing appeals decisions",
            "call center - foreign language interpreter and tty availability",
            "complaints about the drug plan",
            "members choosing to leave the plan (drug plan)",
            "drug plan quality improvement",
            "rating of drug plan",
            "getting needed prescription drugs",
            "mpf price accuracy",
            "medication adherence for diabetes medications",
            "medication adherence for hypertension (ras antagonists)",
            "medication adherence for cholesterol (statins)",
            "mtm program completion rate for cmr"
        ]
        PART_MAP = {
            m: ("D" if m in [
                "complaints about the drug plan",
                "members choosing to leave the plan (drug plan)",
                "drug plan quality improvement",
                "rating of drug plan",
                "getting needed prescription drugs",
                "mpf price accuracy",
                "medication adherence for diabetes medications",
                "medication adherence for hypertension (ras antagonists)",
                "medication adherence for cholesterol (statins)",
                "mtm program completion rate for cmr"
            ] or " (drug plan)" in m or "(ras" in m else "C")
            for m in MEASURES
        }
        THRESHOLDS = {m: {"dir": "high", "cuts": [20, 40, 60, 80]} for m in MEASURES}
        def to_percent(v):
            if pd.isna(v):
                return np.nan
            return float(v * 100.0) if 0.0 <= v <= 1.0 else float(v)
        def assign_star(value_percent, rule):
            if np.isnan(value_percent):
                return np.nan
            cuts = rule["cuts"]
            if rule["dir"] == "high":
                if value_percent < cuts[0]:
                    return 1
                elif value_percent < cuts[1]:
                    return 2
                elif value_percent < cuts[2]:
                    return 3
                elif value_percent < cuts[3]:
                    return 4
                else:
                    return 5
            else:  # lower is better
                if value_percent <= cuts[0]:
                    return 5
                elif value_percent <= cuts[1]:
                    return 4
                elif value_percent <= cuts[2]:
                    return 3
                elif value_percent <= cuts[3]:
                    return 2
                else:
                    return 1
        
        # Select relevant columns for processing
        work_df = df[["member_id", "age"] + [m for m in MEASURES if m in df.columns]].copy()
        
        # Convert measures to numeric
        for c in [m for m in MEASURES if m in work_df.columns]:
            work_df[c] = pd.to_numeric(work_df[c], errors="coerce")
            
        feature_rows = []
        for m in [m for m in MEASURES if m in work_df.columns]:
            vals = work_df[m].dropna().map(to_percent)
            avg_val = vals.mean()
            rule = THRESHOLDS[m]
            star = assign_star(avg_val, rule)
            feature_rows.append({"feature": m, "avg_percent": round(avg_val, 2), "predicted_star": star})

        feature_star_df = pd.DataFrame(feature_rows)
        # return the dataframe instead of saving
        return feature_star_df
