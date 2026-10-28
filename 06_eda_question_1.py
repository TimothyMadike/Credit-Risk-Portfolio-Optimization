
import pandas as pd
import zipfile
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

DATA_FILE = Path("loan_cleaned_sectors.csv")
ZIP_FILE = Path("lending-club-loan-defaulters-prediction.zip")
CSV_NAME = "loan.csv"

CHUNK_SIZE = 50000

categorical_columns = [
    "grade",
    "term",
    "home_ownership",
    "verification_status",
    "purpose"
]

numeric_columns = [
    "int_rate",
    "dti",
    "loan_amnt",
    "annual_inc"
]

required_columns = (
    ["is_bad"] + categorical_columns + numeric_columns
)

# --------------------------------------------------
# FIND THE AVAILABLE DATA SOURCE
# --------------------------------------------------

if DATA_FILE.exists():
    source = "cleaned"
    print("Using cleaned dataset:", DATA_FILE)

elif ZIP_FILE.exists():
    source = "zip"
    print("Cleaned CSV not found.")
    print("Using original CSV inside ZIP as fallback.")

else:
    raise FileNotFoundError(
        "Could not find the cleaned CSV or original ZIP. "
        "Check the file names and working directory."
    )

# --------------------------------------------------
# CHECK COLUMN AVAILABILITY
# --------------------------------------------------

if source == "cleaned":
    available_columns = set(
        pd.read_csv(DATA_FILE, nrows=0).columns
    )
else:
    with zipfile.ZipFile(ZIP_FILE, "r") as z:
        with z.open(CSV_NAME) as f:
            available_columns = set(
                pd.read_csv(f, nrows=0).columns
            )

missing_columns = [
    col for col in required_columns
    if col not in available_columns
]

if missing_columns:
    raise ValueError(
        "These required columns are missing: "
        + ", ".join(missing_columns)
        + ". Check the cleaned dataset and target definition."
    )

# --------------------------------------------------
# CREATE THE BATCH READER
# --------------------------------------------------

def get_reader():
    if source == "cleaned":
        return pd.read_csv(
            DATA_FILE,
            usecols=required_columns,
            chunksize=CHUNK_SIZE,
            low_memory=False
        )

    z = zipfile.ZipFile(ZIP_FILE, "r")
    f = z.open(CSV_NAME)

    # Keep the ZIP and file handles alive while reading.
    reader = pd.read_csv(
        f,
        usecols=required_columns,
        chunksize=CHUNK_SIZE,
        low_memory=False
    )
    return reader, z, f


# --------------------------------------------------
# DEFINE ANALYSIS GROUPS
# --------------------------------------------------

numeric_bins = {
    "int_rate": [
        -float("inf"), 5, 10, 15, 20, float("inf")
    ],
    "dti": [
        -float("inf"), 0, 10, 20, 30, 40, float("inf")
    ],
    "loan_amnt": [
        -float("inf"), 5000, 10000, 15000,
        25000, 35000, float("inf")
    ],
    "annual_inc": [
        -float("inf"), 25000, 50000, 75000,
        100000, 150000, float("inf")
    ]
}

numeric_labels = {
    "int_rate": [
        "Below 5%", "5–10%", "10–15%", "15–20%", "Above 20%"
    ],
    "dti": [
        "Below 0", "0–10", "10–20", "20–30",
        "30–40", "Above 40"
    ],
    "loan_amnt": [
        "Below 5k", "5k–10k", "10k–15k",
        "15k–25k", "25k–35k", "Above 35k"
    ],
    "annual_inc": [
        "Below 25k", "25k–50k", "50k–75k",
        "75k–100k", "100k–150k", "Above 150k"
    ]
}

# Each dictionary stores counts for one feature and group.
aggregates = {}

features = categorical_columns + numeric_columns

for feature in features:
    aggregates[feature] = {}

classified_total = 0
bad_total = 0
good_total = 0
unclassified_total = 0

print("\nStarting EDA Question 1...")
print("Processing records in batches.")

# --------------------------------------------------
# PROCESS THE DATA
# --------------------------------------------------

reader_info = get_reader()

if source == "zip":
    reader, zip_handle, file_handle = reader_info
else:
    reader = reader_info

try:
    for batch_number, chunk in enumerate(reader, start=1):

        # Use only resolved good/bad outcomes.
        chunk["is_bad"] = pd.to_numeric(
            chunk["is_bad"], errors="coerce"
        )

        unclassified_total += int(
            chunk["is_bad"].isna().sum()
        )

        classified = chunk[
            chunk["is_bad"].isin([0, 1])
        ].copy()

        if classified.empty:
            continue

        classified_total += len(classified)
        bad_total += int(
            (classified["is_bad"] == 1).sum()
        )
        good_total += int(
            (classified["is_bad"] == 0).sum()
        )

        # Categorical comparisons
        for feature in categorical_columns:
            values = (
                classified[feature]
                .fillna("Missing/Unknown")
                .astype(str)
            )

            temp = pd.DataFrame({
                "group": values,
                "is_bad": classified["is_bad"]
            })

            summary = temp.groupby("group")["is_bad"].agg(
                loans="count",
                bad_loans="sum"
            )

            for group, row in summary.iterrows():
                if group not in aggregates[feature]:
                    aggregates[feature][group] = [0, 0]

                aggregates[feature][group][0] += int(
                    row["loans"]
                )
                aggregates[feature][group][1] += int(
                    row["bad_loans"]
                )

        # Numeric comparisons
        for feature in numeric_columns:

            values = pd.to_numeric(
                classified[feature]
                .astype(str)
                .str.replace("%", "", regex=False),
                errors="coerce"
            )

            # Exclude invalid DTI values from DTI grouping only.
            if feature == "dti":
                values = values.mask(values < 0)

            grouped = pd.cut(
                values,
                bins=numeric_bins[feature],
                labels=numeric_labels[feature],
                right=False
            )

            temp = pd.DataFrame({
                "group": grouped.astype("object").where(
                    grouped.notna(), "Missing/Invalid"
                ),
                "is_bad": classified["is_bad"]
            })

            summary = temp.groupby(
                "group", observed=True
            )["is_bad"].agg(
                loans="count",
                bad_loans="sum"
            )

            for group, row in summary.iterrows():
                if group not in aggregates[feature]:
                    aggregates[feature][group] = [0, 0]

                aggregates[feature][group][0] += int(
                    row["loans"]
                )
                aggregates[feature][group][1] += int(
                    row["bad_loans"]
                )

        if batch_number % 5 == 0:
            print(
                f"Processed {batch_number * CHUNK_SIZE:,} "
                "or more rows..."
            )

finally:
    if source == "zip":
        file_handle.close()
        zip_handle.close()

# --------------------------------------------------
# REPORT BASELINE
# --------------------------------------------------

baseline = (
    bad_total / classified_total * 100
    if classified_total else 0
)

print("\n========== POPULATION SUMMARY ==========")
print(f"Classified loans: {classified_total:,}")
print(f"Good loans: {good_total:,}")
print(f"Bad loans: {bad_total:,}")
print(f"Unclassified loans: {unclassified_total:,}")
print(f"Bad-loan baseline: {baseline:.2f}%")

# --------------------------------------------------
# EXPORT AND DISPLAY RESULTS
# --------------------------------------------------

output_folder = Path("eda_outputs")
output_folder.mkdir(exist_ok=True)

for feature, groups in aggregates.items():

    rows = []

    for group, counts in groups.items():
        loans, bad_loans = counts

        rate = (
            bad_loans / loans * 100
            if loans else 0
        )

        rows.append({
            "feature": feature,
            "group": str(group),
            "classified_loans": loans,
            "bad_loans": bad_loans,
            "bad_loan_rate_pct": round(rate, 2),
            "difference_from_baseline_pp": round(
                rate - baseline, 2
            )
        })

    result = pd.DataFrame(rows)

    if not result.empty:
        result = result.sort_values(
            "bad_loan_rate_pct",
            ascending=False
        )

    output_path = output_folder / f"{feature}_risk_summary.csv"
    result.to_csv(output_path, index=False)

    print(f"\n========== {feature.upper()} ==========")

    if not result.empty:
        print(result.to_string(index=False))

print("\nResults saved to:", output_folder.resolve())
print("========== EDA QUESTION 1 COMPLETE ==========")
