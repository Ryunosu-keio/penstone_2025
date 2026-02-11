# -*- coding: utf-8 -*-
"""Debug script for multi-baseline analysis"""
import pandas as pd
import numpy as np
import sys
import os

# Add the current directory to path
sys.path.insert(0, '.')

# Set required globals before importing
import builtins
builtins.EXCLUDE_SUBJECTS_MAP = {"Bright": [], "Dark": []}
builtins.DIOPTER_MIN = None
builtins.DIOPTER_MAX = None
builtins.STANDARDIZE_BY_CALIBRATION = False
builtins.USE_DIRECTIONAL_FILTER = False
builtins.IMAGE_KEYS = ["sun_empty", "sun_busy", "rain_empty", "rain_busy"]

# Load data
df = pd.read_excel('../../data/log_with_emr_metrics/lag0p0_mioF100_BLmulti3types_markers/merged/integrated_bright_metrics_n15.xlsx', engine='openpyxl')
print(f'Loaded: {len(df)} rows')

# Quick test of renaming
rename_map = {
    'folder_name': 'subject',
    'process': 'proc',
    'pupil_both_change_rate_mean': 'miosis_rate',
    'BL_stim120_change_rate_mean': 'miosis_rate_stim120',
    'BL_onset120_change_rate_mean': 'miosis_rate_onset120',
    'BL_stim_to_onset_change_rate_mean': 'miosis_rate_sto',
}
df = df.rename(columns=rename_map)

# Check after rename
metrics = ['miosis_rate', 'miosis_rate_stim120', 'miosis_rate_onset120', 'miosis_rate_sto']
print("\n=== After Rename ===")
for m in metrics:
    in_col = m in df.columns
    non_null = df[m].notna().sum() if in_col else 0
    print(f'{m}: in_columns={in_col}, non_null={non_null}')

# Extract image_key (simplified)
IMAGE_KEYS = ["sun_empty", "sun_busy", "rain_empty", "rain_busy"]
def extract_image_key(row):
    for col in ['filename', 'Back_Image_Name_Used']:
        if col in df.columns and pd.notna(row.get(col)):
            for key in IMAGE_KEYS:
                if key in str(row[col]):
                    return key
    return None

df['image_key'] = df.apply(extract_image_key, axis=1)
print(f"\nAfter image_key extraction: {df['image_key'].notna().sum()} rows have image_key")

# Filter
df = df.dropna(subset=['image_key', 'proc'])
print(f"After dropna(image_key, proc): {len(df)} rows")

# Generate z-scores
print("\n=== Z-score Generation ===")
for m in metrics:
    if m in df.columns:
        df[f'z_{m}'] = df.groupby('subject')[m].transform(
            lambda x: (x - x.mean()) / x.std(ddof=1) if x.std(ddof=1) > 0 else 0
        )
        non_null = df[f'z_{m}'].notna().sum()
        print(f'z_{m}: non_null={non_null}')
    else:
        print(f'{m}: NOT IN COLUMNS!')

# Check available
print("\n=== Available Metrics ===")
available = [m for m in metrics if m in df.columns and f'z_{m}' in df.columns]
print(f'Available: {available}')
print(f'Final data rows: {len(df)}')
