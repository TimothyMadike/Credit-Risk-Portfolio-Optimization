
import pandas as pd
import zipfile

zip_path = "lending-club-loan-defaulters-prediction.zip"
csv_filename = "loan.csv"
CHUNK_SIZE = 50000

columns = [
    "annual_inc",
    "dti",
    "revol_util",
    "loan_amnt",
    "loan_status"
]

counts = {
    "zero_income": 0,
    "very_high_income": 0,
    "negative_dti": 0,
    "extreme_dti": 0,
    "high_revol_util": 0
}

examples = {key: [] for key in counts}

print("Investigating unusual financial values...")

with zipfile.ZipFile(zip_path, "r") as z:
    with z.open(csv_filename) as f:
        reader = pd.read_csv(
            f,
            usecols=columns,
            chunksize=CHUNK_SIZE,
            low_memory=True
        )

        for chunk in reader:
            income = chunk["annual_inc"]
            dti = chunk["dti"]
            revol = chunk["revol_util"]

            conditions = {
                "zero_income": income.eq(0),
                "very_high_income": income.ge(10_000_000),
                "negative_dti": dti.lt(0),
                "extreme_dti": dti.ge(100),
                "high_revol_util": revol.gt(100)
            }

            for name, condition in conditions.items():
                counts[name] += int(condition.sum())

                remaining = 10 - len(examples[name])

                if remaining > 0:
                    matches = chunk.loc[condition, columns]
                    examples[name].extend(
                        matches.head(remaining).to_dict("records")
                    )

print("\n========== COUNTS ==========")

for name, count in counts.items():
    print(f"{name}: {count:,}")

print("\n========== SAMPLE RECORDS ==========")

for name, records in examples.items():
    print(f"\n--- {name} ---")

    if records:
        print(pd.DataFrame(records).to_string(index=False))
    else:
        print("No matching records found.")

print("\n========== INVESTIGATION COMPLETE ==========")
