import pandas as pd
from pathlib import Path

def load_hdfs_sequences(data_dir: str):
 """Load normal and abnormal sequences."""
 data_dir = Path(data_dir)
 def _load(name:str) -> pd.DataFrame:
  path = data_dir / name
  df = pd.read_csv(path, header=None, sep=",", names=["block_id", "event_sequence"])
  df["event_sequence"] = df["event_sequence"].astype(str)
  return df
 
 df_normal = _load("hdfs_test_normal")
 df_abnormal = _load("hdfs_test_abnormal")

 X_test = pd.concat(
  [df_normal["event_sequence"], df_abnormal["event_sequence"]],
  ignore_index=True
  )
 y = pd.Series([0] * len(df_normal) + [1] * len(df_abnormal))
 return X_test, y



 
 


  
