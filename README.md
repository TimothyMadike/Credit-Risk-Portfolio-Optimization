# LendingClub Credit Risk Analysis & Portfolio Monitoring

**Tools:** Python · Power BI  
**Domain:** Credit Risk · Financial Services · Portfolio Analytics

## Project Overview

Analysed historical LendingClub loan data to identify borrower and loan characteristics associated with bad-loan risk. The project combines data cleaning, data-quality auditing, exploratory data analysis (EDA) and interactive Power BI reporting to translate large-scale financial data into business insights.

## Business Problem

How can credit-risk teams use historical loan data to identify risk patterns, understand portfolio performance and determine which borrower segments warrant further investigation?

The analysis examines credit grades, interest rates, loan terms, affordability indicators, borrower characteristics and loan purposes.

## Dataset & Methodology

The cleaned dataset contained approximately **2.26 million records and 107 columns**.

Loan outcomes were defined as follows:
- **Bad (1):** Charged Off or Default.
- **Good (0):** Fully Paid.
- **Unclassified:** Current, late, in grace period or other unresolved outcomes, excluded from the binary analysis.

The classified analysis included **1,306,387 loans**:
- Good loans: 1,043,940
- Bad loans: 262,447
- Overall dashboard bad-loan rate: **20.07%**

Python was used for data cleaning, missingness and financial-data audits, outcome classification and EDA. Power BI was used to create interactive KPIs, risk comparisons, a Decomposition Tree and Key Influencers.

## Key Business Findings

### 1. Credit grade shows substantial differences in bad-loan rates

| Grade | Bad-loan rate |
|:---:|---:|
| A | 6.09% |
| B | 13.45% |
| C | 22.51% |
| D | 30.43% |
| E | 38.57% |
| F | 45.25% |
| G | 49.80% |

Grade G had an observed bad-loan rate of 49.80%, compared with 6.09% for Grade A.

**Business implication:** Monitor outcomes by grade and subgrade to identify segments whose realised performance differs from expectations.

### 2. Affordability indicators are associated with risk

- DTI above 40%: **31.78%** bad-loan rate.
- DTI between 0% and 10%: **14.92%**.
- Annual income below $25,000: **24.87%**.
- Annual income above $150,000: **15.06%**.

**Business implication:** Investigate how affordability indicators relate to bad-loan outcomes within comparable credit grades and loan terms.

### 3. Loan term and amount show different risk profiles

- 36-month loans: **16.12%** bad-loan rate.
- 60-month loans: **32.56%**.
- Loans above $35,000: **23.92%**.
- Loans below $5,000: **15.69%**.

**Business implication:** Compare risk across loan terms and sizes while accounting for differences in borrower profiles and credit grades. These observed associations do not establish causation.

### 4. Risk varies by home ownership and loan purpose

- Renters: **23.36%** bad-loan rate, compared with 17.32% for mortgage holders.
- Small-business loans: **29.91%**, compared with 21.27% for debt-consolidation loans.
- Verified income: **23.94%**, compared with 14.77% for income not verified.

**Business implication:** Investigate whether these differences persist after accounting for other borrower and loan characteristics.

### 5. Combined risk factors support deeper investigation

The Power BI Decomposition Tree and Key Influencers allow users to explore combinations of credit grade, interest rate, income, home ownership and loan term.

These visuals help identify segments for further investigation, but their results should be interpreted alongside subgroup sizes, filters and overlapping characteristics.

## Recommendations

1. **Monitor credit grades:** Compare observed bad-loan rates across grades and subgrades.
2. **Investigate affordability:** Examine DTI and income within comparable risk segments.
3. **Compare loan terms:** Investigate differences between 36-month and 60-month loans after accounting for borrower profiles.
4. **Assess financial exposure:** Compare bad-loan rates with funded amounts to distinguish risk levels from potential portfolio impact.
5. **Validate findings:** Test whether observed patterns persist across relevant segments and separate datasets before informing lending decisions.

## Data Quality & Limitations

- Audited missing values, duplicate records, data types and financial outliers.
- Working without direction
- Excluded unresolved loan outcomes from the binary good-versus-bad analysis rather than incorrectly labelling them.
- Results describe historical associations and do not establish causation.
- Missing data, subgroup sizes and differences in borrower composition may affect comparisons.
- The dashboard is an exploratory reporting tool, not a validated default-prediction model.
- Findings from LendingClub should not automatically be generalised to another lender's portfolio.

## Conclusion

The analysis demonstrates an end-to-end credit-risk workflow combining data preparation, outcome classification, exploratory analysis and interactive reporting.

The largest observed differences were across credit grades, with additional risk variation by DTI, income, loan term, loan amount and other borrower characteristics. The dashboard helps stakeholders explore these patterns and identify areas for further investigation, while recognising that additional validation is required before making lending-policy decisions.
