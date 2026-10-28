
import os
import pandas as pd

# ============================================================
# CREDIT RISK INVESTIGATIONS
# Separate dataset for six business investigations
# plus a cumulative high-risk screening funnel.
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "loan_cleaned_sectors.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "credit_risk_investigation_outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR, "credit_risk_investigations.csv"
)
FUNNEL_FILE = os.path.join(
    OUTPUT_DIR, "high_risk_screening_funnel.csv"
)
SUMMARY_FILE = os.path.join(
    OUTPUT_DIR, "investigation_summary.txt"
)

# Only import the columns needed for these investigations.
# emp_length has been added for employment-length analysis.
REQUIRED_COLUMNS = [
    "loan_status",
    "is_bad",
    "emp_length",
    "grade",
    "sub_grade",
    "int_rate",
    "loan_amnt",
    "funded_amnt",
    "purpose",
    "delinq_2yrs",
    "num_tl_90g_dpd_24m",
    "num_accts_ever_120_pd",
    "revol_util",
    "bc_util",
    "percent_bc_gt_75",
    "total_rev_hi_lim",
    "inq_last_6mths",
    "inq_last_12m",
]

# Screening thresholds are analytical choices, not
# official lending policy or validated risk cut-offs.
HIGH_UTILISATION = 75
HIGH_ENQUIRIES_6M = 3
HIGH_ENQUIRIES_12M = 6

print("Starting credit risk investigations...")
print("Reading source data:", INPUT_FILE)

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"Could not find {INPUT_FILE}. "
        "Check that the cleaned CSV is in this folder."
    )

# Read the header first so we can check required columns.
available_columns = pd.read_csv(
    INPUT_FILE, nrows=0
).columns.tolist()

missing_columns = [
    col for col in REQUIRED_COLUMNS
    if col not in available_columns
]

if missing_columns:
    raise ValueError(
        "The source CSV is missing these required columns: "
        + ", ".join(missing_columns)
    )

# Read only the required columns.
df = pd.read_csv(
    INPUT_FILE,
    usecols=REQUIRED_COLUMNS,
    low_memory=False
)

print(f"Rows loaded: {len(df):,}")

# ------------------------------------------------------------
# 1. Prepare numeric fields
# ------------------------------------------------------------

numeric_columns = [
    "is_bad",
    "int_rate",
    "loan_amnt",
    "funded_amnt",
    "delinq_2yrs",
    "num_tl_90g_dpd_24m",
    "num_accts_ever_120_pd",
    "revol_util",
    "bc_util",
    "percent_bc_gt_75",
    "total_rev_hi_lim",
    "inq_last_6mths",
    "inq_last_12m",
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Keep only loans with a known good/bad outcome.
# Do not classify unresolved loan statuses as good.
df = df[df["is_bad"].isin([0, 1])].copy()
df["is_bad"] = df["is_bad"].astype("int8")

print(f"Classified loans retained: {len(df):,}")

# ------------------------------------------------------------
# 2. Create investigation bands and flags
# ------------------------------------------------------------

# Previous delinquency indicators
df["has_previous_delinquency"] = (
    (df["delinq_2yrs"] > 0)
    | (df["num_tl_90g_dpd_24m"] > 0)
    | (df["num_accts_ever_120_pd"] > 0)
).astype("int8")

# Revolving utilisation:
# use the maximum available utilisation indicator.
# Missing values remain missing rather than being treated as 0.
utilisation_columns = [
    "revol_util",
    "bc_util",
    "percent_bc_gt_75",
]

df["revolving_utilisation_max"] = df[
    utilisation_columns
].max(axis=1, skipna=True)

df["high_revolving_utilisation"] = (
    df["revolving_utilisation_max"] >= HIGH_UTILISATION
).astype("Int64")

df.loc[
    df["revolving_utilisation_max"].isna(),
    "high_revolving_utilisation"
] = pd.NA

# Credit enquiry flags
df["high_enquiries_6m"] = (
    df["inq_last_6mths"] >= HIGH_ENQUIRIES_6M
).astype("Int64")

df.loc[
    df["inq_last_6mths"].isna(),
    "high_enquiries_6m"
] = pd.NA

df["high_enquiries_12m"] = (
    df["inq_last_12m"] >= HIGH_ENQUIRIES_12M
).astype("Int64")

df.loc[
    df["inq_last_12m"].isna(),
    "high_enquiries_12m"
] = pd.NA

# Interest-rate bands
df["interest_band"] = pd.cut(
    df["int_rate"],
    bins=[-float("inf"), 10, 15, 20, float("inf")],
    labels=[
        "10% or less",
        "Above 10% to 15%",
        "Above 15% to 20%",
        "Above 20%",
    ],
    right=True
).astype("string")

# Utilisation bands
df["utilisation_band"] = pd.cut(
    df["revolving_utilisation_max"],
    bins=[-float("inf"), 30, 50, 75, 100, float("inf")],
    labels=[
        "30% or less",
        "Above 30% to 50%",
        "Above 50% to 75%",
        "Above 75% to 100%",
        "Above 100%",
    ],
    right=True
).astype("string")

# ------------------------------------------------------------
# 3. Export the separate investigation dataset
# ------------------------------------------------------------

# emp_length is automatically included because it is in
# REQUIRED_COLUMNS and remains in df throughout the script.
df.to_csv(OUTPUT_FILE, index=False)

print("\nInvestigation dataset saved:")
print(OUTPUT_FILE)

# ------------------------------------------------------------
# 4. Build a cumulative high-risk screening funnel
# ------------------------------------------------------------
# Stages are nested:
# Each later stage must pass all previous conditions.
#
# This is an exploratory screening funnel, not a validated
# lending policy. Missing utilisation/enquiry values are not
# counted as meeting the relevant condition.

stage_masks = [
    ("1. All classified loans", pd.Series(True, index=df.index)),
    (
        "2. Previous delinquency",
        df["has_previous_delinquency"].eq(1)
    ),
]

stage_2 = stage_masks[1][1]

stage_3 = (
    stage_2
    & df["high_revolving_utilisation"].eq(1)
)

stage_masks.append(
    ("3. Plus high revolving utilisation", stage_3)
)

stage_4 = (
    stage_3
    & df["high_enquiries_6m"].eq(1)
)

stage_masks.append(
    ("4. Plus frequent enquiries in 6 months", stage_4)
)

funnel_rows = []

for stage_name, mask in stage_masks:
    selected = df.loc[mask]

    total_loans = len(selected)
    bad_loans = int(selected["is_bad"].sum())

    bad_rate = (
        bad_loans / total_loans
        if total_loans > 0 else None
    )

    funded_amount = selected["funded_amnt"].sum(min_count=1)

    funnel_rows.append({
        "stage": stage_name,
        "loan_count": total_loans,
        "bad_loan_count": bad_loans,
        "bad_loan_rate": bad_rate,
        "funded_amount": funded_amount,
    })

funnel = pd.DataFrame(funnel_rows)
funnel.to_csv(FUNNEL_FILE, index=False)

print("\n========== SCREENING FUNNEL ==========")
print(funnel.to_string(index=False))

print("\nFunnel saved:")
print(FUNNEL_FILE)

# ------------------------------------------------------------
# 5. Export summary checks
# ------------------------------------------------------------

summary_lines = [
    "CREDIT RISK INVESTIGATION SUMMARY",
    "=================================",
    f"Classified loans: {len(df):,}",
    f"Good loans: {(df['is_bad'] == 0).sum():,}",
    f"Bad loans: {(df['is_bad'] == 1).sum():,}",
    f"Overall bad-loan rate: {df['is_bad'].mean():.2%}",
    "",
    "SCREENING THRESHOLDS",
    f"High revolving utilisation: >= {HIGH_UTILISATION}%",
    f"High credit enquiries (6 months): >= {HIGH_ENQUIRIES_6M}",
    f"High credit enquiries (12 months): >= {HIGH_ENQUIRIES_12M}",
    "",
    "Important: thresholds are exploratory, not approved lending policy.",
    "The funnel uses only classified loans and does not prove causation.",
    "Funded amount is exposure, not the amount of loss or money saved.",
    "",
    "OUTPUT FILES",
    OUTPUT_FILE,
    FUNNEL_FILE,
]

with open(SUMMARY_FILE, "w", encoding="utf-8") as file:
    file.write("\n".join(summary_lines))

print("\nSummary saved:")
print(SUMMARY_FILE)

print("\nAll investigations completed.")
