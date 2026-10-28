
import pandas as pd
import zipfile

# File configuration
zip_path = 'lending-club-loan-defaulters-prediction.zip'
csv_filename = 'loan.csv'
cleaned_output_path = 'loan_cleaned_sectors.csv'

# 1. Load the dataset directly from the ZIP file
print("Loading raw loan dataset...")

with zipfile.ZipFile(zip_path, 'r') as z:
    df = pd.read_csv(z.open(csv_filename))

print(f"Raw dataset rows: {len(df):,}")

# 2. Remove columns with more than 80% missing values
missing_pct = df.isnull().mean() * 100
cols_to_drop = missing_pct[missing_pct > 80].index.tolist()

df_clean = df.drop(columns=cols_to_drop).copy()

print(f"Columns dropped: {len(cols_to_drop)}")

# 3. Define confirmed outcomes for this initial analysis
bad_statuses = [
    'Charged Off',
    'Does not meet the credit policy. Status:Charged Off',
    'Default'
]

good_statuses = [
    'Fully Paid',
    'Does not meet the credit policy. Status:Fully Paid'
]

def map_risk(status):
    if pd.isna(status):
        return pd.NA
    elif status in bad_statuses:
        return 1
    elif status in good_statuses:
        return 0
    else:
        return pd.NA

# Nullable integer allows 0, 1, and missing values
df_clean['is_bad'] = (
    df_clean['loan_status']
    .apply(map_risk)
    .astype('Int64')
)

print("\n--- Risk Classification Results ---")
print("0 = Fully paid")
print("1 = Confirmed adverse outcome")
print("<NA> = Active, delinquent, or otherwise unclassified")

print(df_clean['is_bad'].value_counts(dropna=False))

# 4. Show all original loan statuses
print("\n--- Original Loan Status Counts ---")
print(df_clean['loan_status'].value_counts(dropna=False))

# 5. Show classification for each status
print("\n--- Loan Status and Risk Classification ---")
audit = (
    df_clean.groupby(
        ['loan_status', 'is_bad'],
        dropna=False
    )
    .size()
    .reset_index(name='loan_count')
)

print(audit.to_string(index=False))

# 6. Calculate the preliminary adverse-outcome rate
classified = df_clean['is_bad'].notna()
classified_count = int(classified.sum())
bad_count = int((df_clean['is_bad'] == 1).sum())
good_count = int((df_clean['is_bad'] == 0).sum())
unclassified_count = int((~classified).sum())

print("\n--- Record Reconciliation ---")
print(f"Total rows: {len(df_clean):,}")
print(f"Fully paid: {good_count:,}")
print(f"Confirmed adverse outcomes: {bad_count:,}")
print(f"Unclassified outcomes: {unclassified_count:,}")
print(
    f"Classified records: {classified_count:,}"
)

if classified_count > 0:
    adverse_rate = bad_count / classified_count * 100
    print(
        f"Adverse-outcome rate among classified records: "
        f"{adverse_rate:.2f}%"
    )
else:
    print("No classified records available to calculate a rate.")

# 7. Save the cleaned dataset
df_clean.to_csv(cleaned_output_path, index=False)

print(f"\nSaved cleaned dataset to: {cleaned_output_path}")
print("Cleaning and audit completed.")

# ==========================================
# PHASE 2: DATA QUALITY AUDIT
# TASK 1: DATASET STRUCTURE AND DUPLICATES
# ==========================================

print("\n========== PHASE 2: DATA QUALITY AUDIT ==========")

# 1. Inspect dataset structure
print("\n--- 1. Dataset Structure ---")

print(f"Total rows: {df_clean.shape[0]:,}")
print(f"Total columns: {df_clean.shape[1]:,}")

print("\nColumn names and data types:")
df_clean.info()

# 2. Check for exact duplicate rows
print("\n--- 2. Exact Duplicate Records ---")

exact_duplicates = df_clean.duplicated().sum()

print(f"Exact duplicate rows: {exact_duplicates:,}")

# 3. Check for duplicate loan IDs
print("\n--- 3. Duplicate Loan ID Check ---")

id_column = next(
    (col for col in ['id', 'loan_id'] if col in df_clean.columns),
    None
)

if id_column is not None:
    print(f"ID column found: {id_column}")

    missing_ids = df_clean[id_column].isna().sum()

    repeated_id_rows = df_clean[id_column].duplicated(
        keep=False
    ).sum()

    print(f"Missing loan IDs: {missing_ids:,}")
    print(f"Rows with repeated IDs: {repeated_id_rows:,}")

else:
    print("No 'id' or 'loan_id' column found.")
    print("We will inspect the column names to identify the correct ID.")

print("\n========== PHASE 2 TASK 1 COMPLETE ==========")

print("\n--- Inspecting Possible ID Columns ---")

print("\nAll column names:")

for column in df_clean.columns:
    print(column)

print("\n========== ID INVESTIGATION ==========")

print("\n--- ID-like columns in original dataset ---")
id_columns = [
    col for col in df.columns
    if "id" in col.lower()
]
print(id_columns if id_columns else "None found")

print("\n--- Columns removed during cleaning ---")
dropped_columns = [
    col for col in df.columns
    if col not in df_clean.columns
]
print(dropped_columns)

print("\n--- Duplicate column names in cleaned data ---")
duplicate_columns = df_clean.columns[
    df_clean.columns.duplicated()
].tolist()
print(duplicate_columns if duplicate_columns else "None found")

print("\n========== INVESTIGATION COMPLETE ==========")


print("\n========== LOAN ID QUALITY CHECK ==========")

for column in ["id", "member_id"]:
    if column in df.columns:
        values = df[column]
        non_missing = values.dropna()

        print(f"\n--- {column} ---")
        print(f"Total rows: {len(values):,}")
        print(f"Missing values: {values.isna().sum():,}")
        print(
            f"Missing percentage: "
            f"{values.isna().mean() * 100:.2f}%"
        )
        print(f"Unique non-missing values: {non_missing.nunique():,}")
        print(
            f"Repeated non-missing ID rows: "
            f"{non_missing.duplicated().sum():,}"
        )

print("\n========== ID QUALITY CHECK COMPLETE ==========")

print("\n========== PHASE 2: MISSING VALUE AUDIT ==========")

missing_audit = pd.DataFrame({
    "missing_count": df_clean.isna().sum(),
    "missing_percentage": df_clean.isna().mean() * 100
})

missing_audit = missing_audit.sort_values(
    by="missing_percentage",
    ascending=False
)

print("\n--- 20 Columns with the Most Missing Values ---")
print(missing_audit.head(20).round(2).to_string())

print("\n--- Overall Missing Value Summary ---")
print(f"Total cells: {df_clean.size:,}")
print(f"Missing cells: {df_clean.isna().sum().sum():,}")
print(
    f"Overall missing percentage: "
    f"{df_clean.isna().sum().sum() / df_clean.size * 100:.2f}%"
)

print("\n--- Columns with More Than 50% Missing Values ---")
high_missing = missing_audit[
    missing_audit["missing_percentage"] > 50
]

print(high_missing.round(2).to_string())

print("\n========== MISSING VALUE AUDIT COMPLETE ==========")

print("\n========== PHASE 2: MISSINGNESS BY LOAN STATUS ==========")

# Check whether next payment date is missing by loan status
payment_missing = df_clean.assign(
    next_payment_missing=df_clean["next_pymnt_d"].isna()
)

payment_missing_summary = (
    payment_missing
    .groupby("loan_status", dropna=False)
    .agg(
        total_loans=("next_pymnt_d", "size"),
        missing_next_payment=("next_payment_missing", "sum")
    )
)

payment_missing_summary["missing_percentage"] = (
    payment_missing_summary["missing_next_payment"]
    / payment_missing_summary["total_loans"] * 100
)

print(
    payment_missing_summary
    .sort_values("missing_percentage", ascending=False)
    .round(2)
    .to_string()
)

print("\n========== MISSINGNESS ANALYSIS COMPLETE ==========")
