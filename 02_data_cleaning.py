import os
import pandas as pd

csv_path = 'lending_club_data/loan.csv'
cleaned_output_path = 'lending_club_data/loan_cleaned_sectors.csv'

print("⏳ Loading raw loan dataset for cleaning...")
df = pd.read_csv(csv_path)

# 1. Drop columns with more than 80% missing data (Cleaning up the clutter)
missing_pct = (df.isnull().sum() / len(df)) * 100
cols_to_drop = missing_pct[missing_pct > 80].index.tolist()
df_clean = df.drop(columns=cols_to_drop)
print(f"🗑️ Dropped {len(cols_to_drop)} columns with >80% missing data.")

# 2. Map 'loan_status' into a clean Binary Risk Flag (1 = Bad/Default, 0 = Good)
# This mimics how a credit analyst defines default events under banking regulations
bad_statuses = [
    'Charged Off', 
    'Late (31-120 days)', 
    'Does not meet the credit policy. Status:Charged Off', 
    'Default'
]

good_statuses = [
    'Fully Paid', 
    'Current', 
    'In Grace Period', 
    'Late (16-30 days)', 
    'Does not meet the credit policy. Status:Fully Paid'
]

def map_risk(status):
    if status in bad_statuses:
        return 1 # Default / Bad Loan
    elif status in good_statuses:
        return 0 # Performing / Good Loan
    else:
        return 0 # Default fallback to safe classification

df_clean['is_bad'] = df_clean['loan_status'].apply(map_risk)
print("🎯 Created 'is_bad' binary target column (Risk Flag).")

# 3. Quick confirmation check
print("\n📊 Cleaned Risk Target Profile:")
print(df_clean['is_bad'].value_counts())
print(df_clean['is_bad'].value_counts(normalize=True) * 100)

# 4. Save the optimized dataset for our upcoming business analysis
print(f"\n💾 Saving cleaned dataset to {cleaned_output_path}...")
df_clean.to_csv(cleaned_output_path, index=False)
print("🎉 Success! Your clean credit framework dataset is ready.")
