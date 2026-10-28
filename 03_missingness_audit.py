
import pandas as pd
import zipfile

zip_path = "lending-club-loan-defaulters-prediction.zip"
csv_filename = "loan.csv"

print("Loading loan data. Please wait...")

with zipfile.ZipFile(zip_path, "r") as z:
    df = pd.read_csv(z.open(csv_filename), usecols=["loan_status", "next_pymnt_d"])

print("\n========== MISSINGNESS BY LOAN STATUS ==========")

df["next_payment_missing"] = df["next_pymnt_d"].isna()

summary = df.groupby("loan_status", dropna=False).agg(
    total_loans=("next_pymnt_d", "size"),
    missing_next_payment=("next_payment_missing", "sum")
)

summary["missing_percentage"] = (
    summary["missing_next_payment"] / summary["total_loans"] * 100
)

print(summary.sort_values("missing_percentage", ascending=False).round(2).to_string())

print("\nAnalysis complete.")
