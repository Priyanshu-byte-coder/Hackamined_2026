"""
Comprehensive data preprocessing pipeline for solar inverter SCADA data.
Reads from ORIGINAL raw CSVs, applies ALL preprocessing, and saves to data_cleaned/.

Steps:
  1. Remove columns with >90% NaN (from findNaN step)
  2. Remove constant-value columns
  3. Drop non-ML metadata columns (_id, createdAt, timestampDate, model, serial, grid_master)
  4. Convert timestamp from epoch ms to IST datetime
  5. Remove duplicate timestamps (data logger re-sends — each row has ALL inverters)
  6. Sort by timestamp
  7. Drop columns with >40% NaN (e.g., temp sensors added mid-collection)
  8. Handle remaining NaN (forward-fill capped at 30 min, then backward-fill edges)
  9. Drop any rows that STILL have NaN after fills
  10. Convert dtypes to float32 for memory efficiency
"""

import os
import re
import pandas as pd
import numpy as np

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "data_cleaned")
REPORT_FILE = os.path.join(os.path.dirname(__file__), "preprocessing_report.txt")

NAN_THRESHOLD = 0.90       # Step 1: Remove columns with >90% NaN
HIGH_NAN_THRESHOLD = 0.40  # Step 7: Remove columns with >40% NaN (post-dedup)
MAX_FFILL_LIMIT = 6        # Max consecutive fills (6 × 5min = 30min gap limit)

# Raw data file mapping
PLANT_FILES = {
    "Plant1_LT1": os.path.join(DATA_DIR, "Plant 1", "Copy of ICR2-LT1-Celestical-10000.73.raws.csv"),
    "Plant1_LT2": os.path.join(DATA_DIR, "Plant 1", "Copy of ICR2-LT2-Celestical-10000.73.raws.csv"),
    "Plant2_AC12": os.path.join(DATA_DIR, "Plant 2", "Copy of 80-1F-12-0F-AC-12.raws.csv"),
    "Plant2_ACBB": os.path.join(DATA_DIR, "Plant 2", "Copy of 80-1F-12-0F-AC-BB.raws.csv"),
    "Plant3_1469": os.path.join(DATA_DIR, "Plant 3", "Copy of 54-10-EC-8C-14-69.raws.csv"),
    "Plant3_146E": os.path.join(DATA_DIR, "Plant 3", "Copy of 54-10-EC-8C-14-6E.raws.csv"),
}


# ── Step 1: Remove >90% NaN columns ─────────────────────────────────────────
def remove_high_nan_columns(df, report, threshold=NAN_THRESHOLD, step="1"):
    """Remove columns where NaN percentage exceeds threshold."""
    nan_pct = df.isnull().sum() / len(df)
    drop_cols = nan_pct[nan_pct > threshold].index.tolist()
    report.append(f"  Step {step} — Dropped {len(drop_cols)} columns with >{threshold*100:.0f}% NaN")
    if drop_cols:
        for c in sorted(drop_cols):
            report.append(f"           {c} ({nan_pct[c]*100:.1f}%)")
    return df.drop(columns=drop_cols)


# ── Step 2: Remove constant-value columns ────────────────────────────────────
def remove_constant_columns(df, report):
    """Remove columns with only one unique value (zero variance)."""
    nunique = df.nunique(dropna=True)
    const_cols = nunique[nunique <= 1].index.tolist()
    report.append(f"  Step 2 — Dropped {len(const_cols)} constant columns")
    if const_cols:
        for c in sorted(const_cols):
            vals = df[c].dropna().unique()
            val_str = str(vals[0]) if len(vals) == 1 else "(all NaN)"
            report.append(f"           {c} = {val_str}")
    return df.drop(columns=const_cols)


# ── Step 3: Drop non-ML columns ─────────────────────────────────────────────
def drop_non_ml_columns(df, report):
    """Remove metadata and string identifier columns with zero ML value."""
    exact_drops = {"_id", "createdAt", "timestampDate", "__v"}
    pattern_drops = re.compile(r"\.(model|serial)$|^grid_master$|^dataLoggerModelId$|^fromServer$|^mac$")

    cols_to_drop = []
    for col in df.columns:
        if col in exact_drops:
            cols_to_drop.append(col)
        elif pattern_drops.search(col):
            cols_to_drop.append(col)

    cols_to_drop = [c for c in cols_to_drop if c in df.columns]
    report.append(f"  Step 3 — Dropped {len(cols_to_drop)} non-ML columns: {sorted(cols_to_drop)}")
    return df.drop(columns=cols_to_drop)


# ── Step 4: Convert timestamp ────────────────────────────────────────────────
def convert_timestamp(df, report):
    """Convert epoch milliseconds to IST datetime."""
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df["timestamp"] = df["timestamp"].dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    ts_min = df["timestamp"].min()
    ts_max = df["timestamp"].max()
    report.append(f"  Step 4 — Timestamp: {ts_min} → {ts_max}")
    return df


# ── Step 5: Remove duplicate timestamps ──────────────────────────────────────
def remove_duplicate_timestamps(df, report):
    """Remove duplicate timestamp rows. Each row has ALL inverters, so dupes are re-sends."""
    before = len(df)
    df = df.drop_duplicates(subset=["timestamp"], keep="last")
    removed = before - len(df)
    report.append(f"  Step 5 — Removed {removed:,} duplicate timestamps ({before:,} → {len(df):,})")
    return df


# ── Step 6: Sort by timestamp ────────────────────────────────────────────────
def sort_by_timestamp(df, report):
    """Ensure chronological order."""
    df = df.sort_values("timestamp").reset_index(drop=True)
    report.append(f"  Step 6 — Sorted by timestamp ✓")
    return df


# ── Step 7: Drop columns with >40% NaN ──────────────────────────────────────
def drop_medium_nan_columns(df, report):
    """
    Drop columns that still have >40% NaN after dedup/sort.
    These are sensors that were added mid-data-collection (e.g., temp, kwh_midnight,
    meter_reactive_power, meter_apparent_power, limit_percent).
    """
    nan_pct = df.isnull().sum() / len(df)
    drop_cols = nan_pct[(nan_pct > HIGH_NAN_THRESHOLD) & (nan_pct <= NAN_THRESHOLD)].index.tolist()
    report.append(f"  Step 7 — Dropped {len(drop_cols)} columns with >{HIGH_NAN_THRESHOLD*100:.0f}% NaN")
    if drop_cols:
        for c in sorted(drop_cols):
            report.append(f"           {c} ({nan_pct[c]*100:.1f}%)")
    return df.drop(columns=drop_cols)


# ── Step 8: Handle remaining NaN ─────────────────────────────────────────────
def handle_nan(df, report):
    """Fill NaN values with appropriate strategies per column type."""
    nan_before = df.isnull().sum().sum()

    alarm_cols = [c for c in df.columns if "alarm_code" in c]
    op_state_cols = [c for c in df.columns if "op_state" in c]
    non_fill_cols = {"timestamp"}

    # Fill alarm_code with 0 (no alarm)
    for col in alarm_cols:
        df[col] = df[col].fillna(0)

    # Forward-fill op_state (state persists until changed)
    for col in op_state_cols:
        df[col] = df[col].ffill(limit=MAX_FFILL_LIMIT)
        df[col] = df[col].bfill(limit=MAX_FFILL_LIMIT)

    # Forward-fill + backward-fill all other numeric columns
    fill_cols = [c for c in df.columns
                 if c not in non_fill_cols
                 and c not in alarm_cols
                 and c not in op_state_cols
                 and df[c].dtype in [np.float64, np.float32, np.int64, np.int32]]

    for col in fill_cols:
        df[col] = df[col].ffill(limit=MAX_FFILL_LIMIT)
        df[col] = df[col].bfill(limit=MAX_FFILL_LIMIT)

    nan_after_fill = df.isnull().sum().sum()
    report.append(f"  Step 8 — NaN: {nan_before:,} → {nan_after_fill:,} (after fill)")
    return df


# ── Step 9: Drop remaining NaN rows ─────────────────────────────────────────
def drop_nan_rows(df, report):
    """Drop rows that still have NaN after fills (gaps > 30 minutes)."""
    before = len(df)
    df = df.dropna()
    dropped = before - len(df)
    report.append(f"  Step 9 — Dropped {dropped:,} rows with unfillable NaN ({before:,} → {len(df):,})")
    return df


# ── Step 10: Convert dtypes ─────────────────────────────────────────────────
def convert_dtypes(df, report):
    """Convert numeric columns to float32, alarm/op_state to int32."""
    mem_before = df.memory_usage(deep=True).sum() / 1024 / 1024

    alarm_cols = [c for c in df.columns if "alarm_code" in c]
    op_state_cols = [c for c in df.columns if "op_state" in c]
    int_like_cols = set(alarm_cols + op_state_cols)

    cols_to_drop = []
    for col in df.columns:
        if col == "timestamp":
            continue
        if col in int_like_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(np.int32)
        elif df[col].dtype == "object":
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().sum() > 0:
                df[col] = converted.astype(np.float32)
            else:
                cols_to_drop.append(col)
        elif df[col].dtype in [np.float64, np.int64]:
            df[col] = df[col].astype(np.float32)

    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
        report.append(f"           Dropped {len(cols_to_drop)} residual string columns: {cols_to_drop}")

    mem_after = df.memory_usage(deep=True).sum() / 1024 / 1024
    report.append(f"  Step 10 — Memory: {mem_before:.1f} MB → {mem_after:.1f} MB ({(1-mem_after/mem_before)*100:.0f}% reduction)")
    return df


# ── Main Pipeline ────────────────────────────────────────────────────────────
def process_file(name, filepath, report):
    """Run all 10 preprocessing steps on a single CSV from raw data."""
    print(f"\n{'='*70}")
    print(f"  Processing: {name}")
    print(f"{'='*70}")

    df = pd.read_csv(filepath, low_memory=False)
    rows_start = len(df)
    cols_start = len(df.columns)

    report.append(f"\n{'='*70}")
    report.append(f"  {name}")
    report.append(f"  Source: {os.path.basename(filepath)}")
    report.append(f"  Input: {rows_start:,} rows × {cols_start} columns")
    report.append(f"{'='*70}")

    # Run full pipeline
    df = remove_high_nan_columns(df, report)          # Step 1
    df = remove_constant_columns(df, report)           # Step 2
    df = drop_non_ml_columns(df, report)               # Step 3
    df = convert_timestamp(df, report)                  # Step 4
    df = remove_duplicate_timestamps(df, report)        # Step 5
    df = sort_by_timestamp(df, report)                  # Step 6
    df = drop_medium_nan_columns(df, report)            # Step 7
    df = handle_nan(df, report)                         # Step 8
    df = drop_nan_rows(df, report)                      # Step 9
    df = convert_dtypes(df, report)                     # Step 10

    # Final stats
    rows_end = len(df)
    cols_end = len(df.columns)
    nan_check = df.isnull().sum().sum()

    report.append(f"  ───────────────────────────────────────────")
    report.append(f"  Output: {rows_end:,} rows × {cols_end} columns")
    report.append(f"  Rows: {rows_start:,} → {rows_end:,} (kept {rows_end/rows_start*100:.1f}%)")
    report.append(f"  Cols: {cols_start} → {cols_end}")
    report.append(f"  Remaining NaN: {nan_check}")
    report.append(f"  Remaining columns: {list(df.columns)}")

    # Console output
    print(f"  {rows_start:,} × {cols_start} cols → {rows_end:,} × {cols_end} cols")
    print(f"  Kept {rows_end/rows_start*100:.1f}% of rows | NaN: {nan_check}")

    # Save cleaned file
    out_path = os.path.join(OUTPUT_DIR, f"{name}_cleaned.csv")
    df.to_csv(out_path, index=False)
    print(f"  💾 Saved: {out_path}")

    return rows_start, rows_end, cols_start, cols_end


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)     

    report = []
    report.append("=" * 70)
    report.append("  COMPLETE DATA PREPROCESSING PIPELINE REPORT")
    report.append("  Processing raw CSVs → ML-ready data")
    report.append("=" * 70)

    summary = {}

    for name, filepath in PLANT_FILES.items():
        if not os.path.exists(filepath):
            print(f"⚠️  File not found: {filepath}")
            report.append(f"\n⚠️  SKIPPED {name}: file not found")
            continue
        r_s, r_e, c_s, c_e = process_file(name, filepath, report)
        summary[name] = (r_s, r_e, c_s, c_e)

    # Overall summary
    report.append(f"\n\n{'='*70}")
    report.append("  OVERALL SUMMARY")
    report.append(f"{'='*70}")
    report.append(f"\n  {'File':<20} {'Input Rows':>12} {'Output Rows':>12} {'Kept%':>7}  {'In Cols':>8} {'Out Cols':>9}")
    report.append(f"  {'-'*20} {'-'*12} {'-'*12} {'-'*7}  {'-'*8} {'-'*9}")

    print(f"\n\n{'='*70}")
    print("  OVERALL SUMMARY")
    print(f"{'='*70}")

    for name, (r_s, r_e, c_s, c_e) in summary.items():
        pct = r_e / r_s * 100 if r_s > 0 else 0
        report.append(f"  {name:<20} {r_s:>12,} {r_e:>12,} {pct:>6.1f}%  {c_s:>8} {c_e:>9}")
        print(f"  {name:<20}  {r_s:>7,} → {r_e:>7,} rows ({pct:.0f}%)  |  {c_s:>3} → {c_e:>3} cols")

    # Save report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    print(f"\n📄 Report saved: {REPORT_FILE}")


if __name__ == "__main__":
    main()
