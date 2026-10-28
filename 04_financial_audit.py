
import pandas as pd
import zipfile

zip_path = "lending-club-loan-defaulters-prediction.zip"
csv_filename = "loan.csv"

columns_to_check = [
    "loan_amnt",
    "funded_amnt",
    "funded_amnt_inv",
    "int_rate",
    "installment",
    "annual_inc",
    "dti",
    "revol_util",
    "total_pymnt",
    "total_pymnt_inv",
    "loan_status"
]

numeric_columns = [
    "loan_amnt",
    "funded_amnt",
    "funded_amnt_inv",
    "int_rate",
    "installment",
    "annual_inc",
    "dti",
    "revol_util",
    "total_pymnt",
    "total_pymnt_inv"
]

# Process 50,000 rows at a time
CHUNK_SIZE = 50000

total_rows = 0

missing_counts = {col: 0 for col in columns_to_check}
negative_counts = {col: 0 for col in numeric_columns}
zero_counts = {col: 0 for col in numeric_columns}
invalid_counts = {col: 0 for col in numeric_columns}

minimums = {col: None for col in numeric_columns}
maximums = {col: None for col in numeric_columns}

print("Starting memory-efficient financial audit...")
print("Reading the CSV in batches of", CHUNK_SIZE, "rows.")

with zipfile.ZipFile(zip_path, "r") as z:
    with z.open(csv_filename) as f:

        reader = pd.read_csv(
            f,
            usecols=columns_to_check,
            chunksize=CHUNK_SIZE,
            low_memory=True
        )

        for chunk_number, chunk in enumerate(reader, start=1):

            total_rows += len(chunk)

            # Missing-value counts
            for col in columns_to_check:
                missing_counts[col] += int(chunk[col].isna().sum())

            # Numeric validity checks
            for col in numeric_columns:

                values = pd.to_numeric(
                    chunk[col],
                    errors="coerce"
                )

                # Count non-empty values that cannot be converted
                invalid_counts[col] += int(
                    (chunk[col].notna() & values.isna()).sum()
                )

                valid = values.dropna()

                if not valid.empty:

                    batch_min = valid.min()
                    batch_max = valid.max()

                    if minimums[col] is None:
                        minimums[col] = batch_min
                        maximums[col] = batch_max
                    else:
                        minimums[col] = min(
                            minimums[col], batch_min
                        )
                        maximums[col] = max(
                            maximums[col], batch_max
                        )

                    negative_counts[col] += int(
                        (valid < 0).sum()
                    )

                    zero_counts[col] += int(
                        (valid == 0).sum()
                    )

            if chunk_number % 5 == 0:
                print(
                    f"Processed {total_rows:,} rows..."
                )

print("\n========== FINANCIAL MISSING VALUE AUDIT ==========")

for col in columns_to_check:
    missing = missing_counts[col]
    percentage = (
        missing / total_rows * 100
        if total_rows else 0
    )

    print(
        f"{col}: {missing:,} missing "
        f"({percentage:.2f}%)"
    )

print("\n========== NUMERIC VALIDITY AUDIT ==========")

for col in numeric_columns:
    print(f"\n{col}")
    print(f"  Minimum: {minimums[col]}")
    print(f"  Maximum: {maximums[col]}")
    print(f"  Negative values: {negative_counts[col]:,}")
    print(f"  Zero values: {zero_counts[col]:,}")
    print(
        f"  Non-numeric, non-missing values: "
        f"{invalid_counts[col]:,}"
    )

print("\nTotal rows processed:", f"{total_rows:,}")
print("========== AUDIT COMPLETE ==========")
