import re
from pathlib import Path
import pandas as pd
import json

LOG_PATH = Path("data/hdfs_loghub/HDFS.log")
LABEL_PATH = Path("data/hdfs_loghub/anomaly_label.csv")
OUT_DIR = Path("artifacts")

BLOCK_RE = re.compile(r"(blk_-?\d+)")
IP_PORT_RE = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?\b")
NUMBER_RE = re.compile(r"\b\d+\b")


def extract_block_id(line: str):
    match = BLOCK_RE.search(line)
    return match.group(1) if match else None


def extract_message(line: str):
    parts = line.strip().split(" ", 5)
    if len(parts) < 6:
        return None
    return parts[5]


def normalize_message(message: str) -> str:
    message = BLOCK_RE.sub("<*>", message)
    message = IP_PORT_RE.sub("<*>", message)
    message = NUMBER_RE.sub("<*>", message)
    return message


def load_labels():
    labels_df = pd.read_csv(LABEL_PATH)
    labels_df = labels_df.rename(columns={"BlockId": "block_id", "Label": "label"})
    return labels_df


def save_template_mapping(template_to_id: dict, path: Path):
    with open(path, "w") as f:
        json.dump(template_to_id, f, indent=2)


def load_template_mapping(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def parse_raw_logs() -> pd.DataFrame:
    rows = []

    with open(LOG_PATH, "r") as f:
        for line_num, line in enumerate(f, start=1):
            block_id = extract_block_id(line)
            if not block_id:
                continue

            message = extract_message(line)
            if message is None:
                continue
            template = normalize_message(message)

            rows.append(
                {"line_num": line_num, "block_id": block_id, "template": template}
            )
    return pd.DataFrame(rows)


def build_sequences(parsed_df: pd.DataFrame, mapping_path: Path):
    if mapping_path.exists():
        template_to_id = load_template_mapping(mapping_path)
    else:
        template_to_id = {}

    unique_templates = sorted(parsed_df["template"].unique())

    next_id = max(template_to_id.values(), default=0) + 1
    for tpl in unique_templates:
        if tpl not in template_to_id:
            template_to_id[tpl] = next_id
            next_id = next_id + 1

    save_template_mapping(template_to_id, mapping_path)

    parsed_df["event_id"] = parsed_df["template"].map(template_to_id)

    sequences_df = (
        parsed_df.groupby("block_id")["event_id"]
        .apply(lambda x: " ".join(str(event_id) for event_id in x.tolist()))
        .reset_index()
        .rename(columns={"event_id": "event_sequence"})
    )

    templates_df = (
        pd.DataFrame(
            {
                "template": list(template_to_id.keys()),
                "event_id": list(template_to_id.values()),
            }
        )
        .sort_values("event_id")
        .reset_index(drop=True)
    )
    return sequences_df, templates_df


def main():
    OUT_DIR.mkdir(exist_ok=True)
    parsed_df = parse_raw_logs()

    mapping_path = OUT_DIR
    sequences_df, templates_df = build_sequences(parsed_df)
    labels_df = load_labels()
    final_df = sequences_df.merge(labels_df, on="block_id", how="left")

    print("Missing labels:", final_df["label"].isna().sum())

    final_df.to_csv(OUT_DIR / "hdfs_sequences.csv", index=False)
    templates_df.to_csv(OUT_DIR / "hdfs_templates.csv", index=False)


if __name__ == "__main__":
    main()
