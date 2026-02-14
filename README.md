# HDFS Log Anomaly Detection

## Dataset

This project uses the HDFS dataset from Loghub:
https://github.com/ait-aecid/anomaly-detection-log-datasets

Download instructions:
cd hdfs_loghub/
wget https://zenodo.org/record/3227177/files/HDFS_1.tar.gz
tar -xvf HDFS_1.tar.gz 

## Overview
Exploring anomaly detection techniques on the HDFS log dataset from LogHub.

## Current Progress
- Loaded preprocessed HDFS sequences
- Engineered sequence length feature
- Compared distribution between normal and abnormal sequences
- Identified event IDs disproportionately common in abnormal sequences (e.g., 27, 28)

## Next Steps
- Build bag-of-events feature representation
- Train simple baseline classifier
- Evaluate performance