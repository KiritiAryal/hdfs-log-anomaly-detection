# HDFS Log Anomaly Detection

A machine learning project for detecting anomalous behavior in HDFS logs using log parsing, event-sequence representation, and supervised classification.

The project explores an end-to-end workflow for transforming raw system logs into structured machine-learning features and evaluating whether event patterns can distinguish normal from anomalous HDFS block behavior.

## Project Overview

Raw system logs are difficult to use directly as machine-learning input because they contain variable information such as block IDs, IP addresses, ports, timestamps, and file paths.

This project transforms the raw HDFS logs into structured event sequences:

```text
Raw HDFS logs
      ↓
Log parsing
      ↓
Message normalization
      ↓
Event templates
      ↓
Event IDs
      ↓
Block-level event sequences
      ↓
Bag-of-events features
      ↓
Logistic Regression
      ↓
Normal / Anomalous
```

The goal is to build an understandable and reproducible baseline rather than treating the anomaly detector as a black box.

## Dataset

This project uses the HDFS dataset from Loghub:
https://github.com/ait-aecid/anomaly-detection-log-datasets

Download instructions:
cd hdfs_loghub/
wget https://zenodo.org/record/3227177/files/HDFS_1.tar.gz
tar -xvf HDFS_1.tar.gz

## Overview

Exploring anomaly detection techniques on the HDFS log dataset from LogHub.

A separate label file provides the ground-truth label associated with each HDFS block ID.

This allows the project to construct block-level sequences and evaluate the model against known normal/anomalous labels.

## 1. Log Parsing

The raw HDFS log is first parsed into structured records.

The parser extracts information such as:

- Block ID
- Event template
- Event ID
- Timestamp
- Ground-truth label

Variable portions of messages are normalized so that structurally similar messages can be represented by the same event template.

For example, messages such as:

```text
Receiving block blk_123 ...
Receiving block blk_456 ...
```

represent the same type of event even though the block IDs are different.

They can therefore be normalized into a common template:

```text
Receiving block <*> ...
```

## 2. Event Templates and Event IDs

Each unique normalized event template is assigned an integer event ID.

For example:

```text
Template                                      Event ID
-------------------------------------------------------
PacketResponder <*> for block <*> terminating     1
Received block <*> of size <*> from <*>            2
Receiving block <*> src: <*> dest: <*>             3
```

A parsed block can therefore be represented as a sequence of event IDs:

```text
blk_123 → 3 1 3 2 2 4
```

The sequence preserves the order in which the events occurred for that block.

A persistent template-to-ID mapping is saved so that event IDs remain reproducible when processing additional logs.

## 3. Block-Level Sequence Construction

The HDFS block ID is used as the sequence identifier.

All events associated with the same block are grouped together in their original log order.

For example:

```text
blk_123
    ↓
Event 3
Event 1
Event 3
Event 2
Event 2
Event 4
```

becomes:

```text
3 1 3 2 2 4
```

The resulting dataset contains one row per block:

| block_id | event_sequence | label     |
| -------- | -------------- | --------- |
| blk_123  | 3 1 3 2 2 4    | Normal    |
| blk_456  | 3 1 7 2 9      | Anomalous |

## 4. Feature Representation

The event sequences are converted into numerical features using a bag-of-events representation.

Each event ID becomes a feature.

For example:

```text
Sequence:
3 1 3 2 2 4
```

can be represented approximately as:

```text
event 1 → 1
event 2 → 2
event 3 → 2
event 4 → 1
```

This produces a sparse feature matrix where:

- Rows represent HDFS block sequences
- Columns represent event IDs
- Values represent event occurrences

The resulting matrix is highly sparse because each sequence contains only a small subset of all possible event types.

## 5. Classification

The current baseline model is Logistic Regression.

The training workflow uses a scikit-learn Pipeline containing:

```text
CountVectorizer
      ↓
LogisticRegression
```

The data is split into training and testing sets using a stratified split so that the normal/anomalous class distribution is preserved.

Class weighting is enabled to account for the imbalance between normal and anomalous sequences.

## 6. Model Evaluation

The current baseline produced the following results on the held-out test set:

| Metric            | Result  |
| ----------------- | ------- |
| Accuracy          | 99.88%  |
| ROC AUC           | 0.99958 |
| Normal precision  | 100.00% |
| Normal recall     | 99.88%  |
| Anomaly precision | 96.15%  |
| Anomaly recall    | 100.00% |
| Anomaly F1        | 98.04%  |

Confusion matrix:

```text
                 Predicted
              Normal   Anomaly

Actual Normal  110393      135
Actual Anomaly      0     3368
```

The model correctly identified all anomalous sequences in this particular evaluation split, while producing 135 false positives.

Because the dataset is imbalanced, accuracy alone is not used to evaluate the model. Precision, recall, F1-score, confusion matrix, and ROC AUC are also examined.

## 7. Model Interpretability

One advantage of using Logistic Regression as a baseline is that its learned coefficients can be inspected.

Positive coefficients indicate event features that push the prediction toward the anomalous class, while negative coefficients push the prediction toward the normal class.

This allows the project to identify event IDs that are most strongly associated with each class.

For example, preliminary frequency analysis showed that several events, including event IDs `27`, `28`, and `20`, occur disproportionately more frequently in anomalous sequences.

The next step is to compare these frequency-based observations with the Logistic Regression coefficients.

## 8. Reproducibility

The project is being structured so that parsing and model training can be reproduced from the raw data.

Important generated artifacts include:

```text
artifacts/
├── hdfs_sequences.csv
├── hdfs_templates.csv
├── template_to_id.json
├── model.joblib
└── metrics.json
```

The template mapping is persisted so that the same event templates can retain consistent event IDs across subsequent runs.

## Project Structure

```text
.
├── data/
│   └── HDFS/
│       └── HDFS.log
│
├── src/
│   ├── data.py
│   ├── parse_hdfs.py
│   └── train.py
│
├── artifacts/
│   ├── hdfs_sequences.csv
│   ├── hdfs_templates.csv
│   ├── template_to_id.json
│   ├── model.joblib
│   └── metrics.json
│
├── requirements.txt
├── Makefile
└── README.md
```

Large raw datasets and generated artifacts are excluded from version control where appropriate.

## Technologies

- Python
- pandas
- NumPy
- scikit-learn
- Matplotlib
- joblib
- Regular expressions
- Git / GitHub

## Current Status

### Completed

- [x] Load and inspect HDFS data
- [x] Explore sequence-length distributions
- [x] Compare event frequencies between normal and anomalous sequences
- [x] Build bag-of-events features
- [x] Train Logistic Regression baseline
- [x] Evaluate using confusion matrix, precision, recall, F1, and ROC AUC
- [x] Inspect model coefficients
- [x] Begin converting the workflow into reproducible scripts
- [x] Implement persistent template-to-event-ID mapping

### In Progress

- [ ] Parse the complete raw HDFS log
- [ ] Validate parsed sequences against the provided ground-truth labels
- [ ] Improve parser robustness
- [ ] Complete reproducible `parse → train → evaluate` workflow
- [ ] Add automated tests
- [ ] Compare alternative feature representations
- [ ] Compare additional anomaly-detection/classification approaches

## Why This Project?

This project is part of my effort to build stronger practical experience in software engineering, Python, machine learning, and systems/log analysis.

Rather than only training a model on an already-prepared dataset, the project focuses on the complete engineering workflow:

```text
Raw data
→ Parsing
→ Data validation
→ Feature engineering
→ Model training
→ Evaluation
→ Interpretation
→ Reproducibility
```

The goal is to understand each stage well enough to explain and implement it rather than treating machine-learning libraries as black boxes.

## Future Work

Potential extensions include:

- Sequence-aware representations instead of simple bag-of-events features
- TF-IDF feature representations
- N-gram features to capture event ordering
- Tree-based models
- Unsupervised anomaly detection
- Sequence models
- Precision/recall analysis at different classification thresholds
- Cross-validation
- Parser unit tests
- Performance profiling on the complete HDFS dataset
- Improved handling of previously unseen event
  templates
- Build an observability dashboard using Grafana and Prometheus to monitor model and pipeline behavior, including prediction volumes, anomaly rates, false-positive/false-negative trends, parsing errors, processing latency, and data quality metrics
