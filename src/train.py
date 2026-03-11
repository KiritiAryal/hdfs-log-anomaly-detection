import json
import pandas as pd
from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from src.data import load_hdfs_sequences
import joblib
 

def get_top_events(pipeline: Pipeline, count: int):
 vectorizer = pipeline.named_steps["vectorizer"]
 clf = pipeline.named_steps["classifier"]

 feature_names = vectorizer.get_feature_names_out()
 weights = clf.coef_[0]

 weights_df = pd.DataFrame({
  "event": feature_names, "weight": weights
  }).sort_values("weight")

 print("Top abnormal-indicating events:")
 print(weights_df.tail(count)[::-1].to_string(index=False))  
 print("\nTop normal-indicating events:")
 print(weights_df.head(count).to_string(index=False))

def build_pipeline():
 """Build ML Pipeline"""
 pipeline = Pipeline([
  ("vectorizer", CountVectorizer(token_pattern=r"\S+", binary=True)),
  ("classifier", LogisticRegression(max_iter=2000, class_weight = "balanced"))
  ])
 return pipeline

def train():
 X, y = load_hdfs_sequences("data/HDFS")
 X_train, X_test, y_train, y_test = train_test_split(
  X,
  y,
  test_size=0.2, 
  random_state=42, 
  stratify=y
  )
 pipeline = build_pipeline()
 pipeline.fit(X_train, y_train)

 y_pred = pipeline.predict(X_test)
 y_proba = pipeline.predict_proba(X_test)[:, 1]
 
 cm = confusion_matrix(y_test, y_pred)
 report = classification_report(y_test, y_pred, digits=4)
 roc = roc_auc_score(y_test, y_proba)
 print(cm)
 print(report)
 print("ROC: ", roc)
 
 out_dir = Path("artifacts")
 out_dir.mkdir(exist_ok=True)
 joblib.dump(pipeline, out_dir / "model.joblib")

 metrics = {"confusion_matrix": cm.tolist(), "classification_report": report, "ROC": float(roc)}
 (out_dir/"metrics.json").write_text(json.dumps(metrics, indent=2))
 get_top_events(pipeline, 10)

if __name__ == "__main__":
 train()
