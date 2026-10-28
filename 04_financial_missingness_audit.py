
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

print("Loading financial columns...")

with zipfile.ZipFile(zip_path, "r") as z:
    with z.open(csv_filename) as f:
        df = pd.read_csv(
            f,
            usecols=columns_to_check,
            low_memory=False
        )

print("\n========== FINANCIAL MISSING VALUE AUDIT ==========")

audit = pd.DataFrame({
    "missing_count": df.isna().sum(),
    "missing_percentage": df.isna().mean() * 100
})

print(audit.round(2).to_string())

print("\n========== AUDIT COMPLETE ==========")

import pandas as pd
import zipfile

zip_path = "lending-club-loan-defaulters-prediction.zip"
csv_filename = "loan.csv"

columns = [
    "loan_amnt",
    "funded_amnt",
    "int_rate",
    "installment",
    "annual_inc",
    "dti",
    "revol_util",
    "total_pymnt",
    "loan_status"
]

print("Loading data for validity checks...")

with zipfile.ZipFile(zip_path, "r") as z:
    with z.open(csv_filename) as f:
        df = pd.read_csv(f, usecols=columns, low_memory=False)

print("\n========== NUMERIC DATA VALIDITY AUDIT ==========")

numeric_columns = [
    "loan_amnt",
    "funded_amnt",
    "int_rate",
    "installment",
    "annual_inc",
    "dti",
    "revol_util",
    "total_pymnt"
]

print("\n--- Minimum and Maximum Values ---")
print(df[numeric_columns].describe().loc[["min", "max"]].round(2).to_string())

print("\n--- Negative Values ---")
for col in numeric_columns:
    count = (df[col] < 0).sum()
    print(f"{col}: {count:,} negative values")

print("\n--- Zero Values ---")
for col in numeric_columns:
    count = (df[col] == 0).sum()
    print(f"{col}: {count:,} zero values")

print("\n========== AUDIT COMPLETE ==========")
