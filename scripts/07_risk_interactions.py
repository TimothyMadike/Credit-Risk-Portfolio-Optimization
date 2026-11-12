
import pandas as pd
import zipfile
from pathlib import Path

# --------------------------------------------------
# 1. File paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "loan_cleaned_sectors.csv"
OUTPUT_DIR = BASE_DIR / "eda_outputs"

OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "loan_risk_interactions.csv"

# --------------------------------------------------
# 2. Columns needed for risk interaction analysis
# --------------------------------------------------

REQUIRED_COLUMNS = [
    "loan_status",
    "grade",
    "int_rate",
    "term",
    "dti",
    "home_ownership",
    "annual_inc",
]

# --------------------------------------------------
# 3. Read only the required columns
# --------------------------------------------------

print("Starting risk interaction dataset preparation...")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Could not find the cleaned dataset: {INPUT_FILE}"
    )

df = pd.read_csv(
    INPUT_FILE,
    usecols=lambda col: col in REQUIRED_COLUMNS,
    low_memory=False
)

missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Required columns missing from dataset: {sorted(missing_columns)}"
    )

print(f"Rows loaded: {len(df):,}")
print(f"Columns loaded: {len(df.columns)}")


# --------------------------------------------------
# 4. Create a reliable target
# --------------------------------------------------

df["loan_status"] = (
    df["loan_status"].astype("string").str.strip()
)

df["is_bad"] = pd.Series(
    pd.NA, index=df.index, dtype="Int64"
)

good_statuses = [
    "Fully Paid",
    "Does not meet credit policy. Status:Fully Paid"
]

bad_statuses = [
    "Charged Off",
    "Default",
    "Does not meet credit policy. Status:Charged Off"
]

df.loc[
    df["loan_status"].isin(good_statuses), "is_bad"
] = 0

df.loc[
    df["loan_status"].isin(bad_statuses), "is_bad"
] = 1

# Keep only resolved outcomes.
df = df[df["is_bad"].notna()].copy()
df["is_bad"] = df["is_bad"].astype("int8")

print(f"Classified loans retained: {len(df):,}")
print(f"Good loans: {(df['is_bad'] == 0).sum():,}")
print(f"Bad loans: {(df['is_bad'] == 1).sum():,}")
print(f"Bad-loan rate: {df['is_bad'].mean() * 100:.2f}%")


# --------------------------------------------------
# 5. Clean and create analysis bands
# --------------------------------------------------

df["int_rate"] = pd.to_numeric(df["int_rate"], errors="coerce")
df["dti"] = pd.to_numeric(df["dti"], errors="coerce")
df["annual_inc"] = pd.to_numeric(df["annual_inc"], errors="coerce")

df["grade"] = df["grade"].astype("string").str.strip()
df["term"] = df["term"].astype("string").str.strip()
df["home_ownership"] = (
    df["home_ownership"].astype("string").str.strip()
)

# Interest-rate bands (int_rate is expressed in percentage points)
df["interest_band"] = pd.cut(
    df["int_rate"],
    bins=[-float("inf"), 5, 10, 15, 20, float("inf")],
    labels=["<=5%", ">5-10%", ">10-15%", ">15-20%", ">20%"],
    right=True
)

# DTI bands: retain negative or extreme values as visible audit categories.
df["dti_band"] = pd.cut(
    df["dti"],
    bins=[-float("inf"), 0, 10, 20, 30, 40, float("inf")],
    labels=[
        "<=0",
        ">0-10",
        ">10-20",
        ">20-30",
        ">30-40",
        ">40"
    ],
    right=True
)

# Annual-income bands
df["income_band"] = pd.cut(
    df["annual_inc"],
    bins=[-float("inf"), 25000, 50000, 75000, 100000, 150000, float("inf")],
    labels=[
        "<=$25k",
        ">$25k-$50k",
        ">$50k-$75k",
        ">$75k-$100k",
        ">$100k-$150k",
        ">$150k"
    ],
    right=True
)

# Keep only the fields needed for interactive analysis.
OUTPUT_COLUMNS = [
    "is_bad",
    "grade",
    "term",
    "interest_band",
    "dti_band",
    "income_band",
    "home_ownership",
]

df = df[OUTPUT_COLUMNS].copy()

# Drop records missing the factors needed for a given visual
# in Power BI, each visual can filter missing factor values.
df.to_csv(OUTPUT_FILE, index=False)

print("\n========== OUTPUT SUMMARY ==========")
print(f"Output file: {OUTPUT_FILE}")
print(f"Output rows: {len(df):,}")
print(f"Output columns: {len(df.columns)}")
print(f"Output size: {OUTPUT_FILE.stat().st_size / (1024 ** 2):.2f} MB")
print("\nMissing values by column:")
print(df.isna().sum().to_string())
print("\nDataset preparation complete.")
