import pandas as pd
from pathlib import Path
import joblib


def score():
    model_path = Path("artifacts/model.joblib")
    pipeline = joblib.load(model_path)

    input_path = Path("data/HDFS/hdfs_train")
    df = pd.read_csv(
        input_path, sep=",", header=None, names=["block_id", "event_sequence"]
    )
    df["event_sequence"] = df["event_sequence"].astype(str)

    proba = pipeline.predict_proba(df["event_sequence"])[:, 1]
    df_out = df.copy()
    df_out["anomaly_prob"] = proba

    out_path = Path("artifacts/scored.csv")
    df_out.to_csv(out_path, index=False)


if __name__ == "__main__":
    score()
