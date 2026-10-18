import os
import pandas as pd

cleaned_file = 'lending_club_data/loan_cleaned_sectors.csv'
powerbi_out = 'lending_club_data/powerbi_dashboard_data.csv'

print("⏳ Fresh start: Calculating all banking metrics inside Python...")
df = pd.read_csv(cleaned_file, low_memory=False)

# Clean public derogatory records into clear buckets
def bucket_pub_rec(val):
    if pd.isnull(val) or val == 0: return '0 Records'
    elif val == 1: return '1 Record'
    else: return '2+ Records'

df['derogatory_history'] = df['pub_rec'].apply(bucket_pub_rec)

# Group the data and calculate everything here (Zero DAX needed)
powerbi_df = df.groupby([
    'grade', 'term', 'home_ownership', 'purpose', 
    'emp_length', 'application_type', 'derogatory_history'
]).agg(
    total_accounts=('loan_amnt', 'count'),
    total_capital_funded=('funded_amnt', 'sum'),
    monthly_cash_pipeline=('installment', 'sum'),
    total_defaults=('is_bad', 'sum')
).reset_index()

# Calculate the final risk rate column inside Python
powerbi_df['portfolio_bad_rate_pct'] = (powerbi_df['total_defaults'] / powerbi_df['total_accounts']) * 100

# Fill any empty gaps with zero
powerbi_df.fillna(0, inplace=True)

powerbi_df.to_csv(powerbi_out, index=False)
print("🎉 Clean data model successfully written to CSV with pre-calculated metrics!")
