# Data Quality Report

## 1. Overview

This report documents the data-quality checks performed during the LendingClub Credit Risk Analysis project.

The purpose of the audits was to identify missing, invalid, unusual and potentially unreliable values before conducting exploratory analysis.

The approach prioritised documenting data-quality issues and preserving the distinction between valid, questionable and unresolved records.

## 2. Dataset Overview

The cleaned working dataset contained approximately 2.26 million loan records and 107 columns.

For binary loan-performance analysis, outcomes were classified as follows:

| Loan category | Records |
|---|---:|
| Good loans | 1,043,940 |
| Bad loans | 262,447 |
| Classified loans | 1,306,387 |
| Unclassified loans | 954,281 |

Unclassified records included loans with statuses such as Current, Late and Grace Period, as well as other unresolved outcomes.

These records were excluded from binary good/bad outcome analysis rather than being assigned an assumed outcome.

## 3. Data Quality Checks

### 3.1 Missingness Assessment

A missingness audit was conducted to identify incomplete fields and assess their potential impact on the analysis.

Missing values were documented and considered when selecting fields and interpreting results.

The audit supported a more informed approach to data preparation rather than automatically removing every column or record containing missing values.

### 3.2 Financial Data Validation

Financial and numerical fields were examined for unusual values, zero values, negative values and extreme observations.

The audit identified the following:

| Field | Observed issue |
|---|---|
| Annual income (`annual_inc`) | Minimum value of 0; 1,667 zero values |
| Debt-to-income ratio (`dti`) | Minimum -1; maximum 999; 2 negative values |
| Revolving utilisation (`revol_util`) | Maximum value of 892.3; 13,069 zero values |
| Total payments (`total_pymnt`) | 1,008 zero values |
| Total payments to investors (`total_pymnt_inv`) | 1,286 zero values |

These observations were flagged for consideration because unusual values can affect financial analysis and interpretation.

### 3.3 Extreme Values

Numerical fields were reviewed for unusually large or small observations.

Extreme values were not automatically assumed to be errors. Their interpretation depends on the field, its business meaning and the context in which the observation occurred.

## 4. Data Preparation Decisions

The following principles guided the analysis:

- Good and bad loan outcomes were explicitly defined using the available loan statuses.
- Unresolved loan statuses were kept separate from the binary outcome classification.
- Missing and questionable values were assessed rather than automatically treated as valid.
- Unusual financial values were documented for transparency.
- Analytical conclusions were based on the classified loan population.

## 5. Impact on the Analysis

The classification approach produced a population of 1,306,387 loans for binary outcome analysis.

Within this population:

- Good loans accounted for 1,043,940 records.
- Bad loans accounted for 262,447 records.
- The observed bad-loan rate was approximately 20.07%.

The remaining 954,281 records were excluded from binary outcome calculations because their outcomes were unresolved or did not meet the classification criteria.

## 6. Limitations

- Historical data may contain incomplete, inaccurate or inconsistently recorded values.
- Some unusual observations may represent genuine borrower or loan characteristics.
- Missing values can affect the available population for individual analyses.
- Excluding unresolved outcomes means the classified population does not represent every record in the original dataset.
- Data-quality checks reduce the risk of misleading analysis but do not guarantee that every underlying issue has been identified.

## 7. Conclusion

The data-quality process established a documented foundation for the LendingClub analysis.

By assessing missingness, checking financial fields, reviewing unusual observations and keeping unresolved loan statuses separate, the project aimed to produce more transparent and reliable exploratory findings.
