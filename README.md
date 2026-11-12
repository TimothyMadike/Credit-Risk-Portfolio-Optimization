# LendingClub Credit Risk Analysis & Portfolio Monitoring

**Tools:** Python · Power BI  
**Domain:** Credit Risk · Financial Services · Portfolio Analytics

# LendingClub Credit Risk Analysis & Portfolio Monitoring

## Project Overview

This project analyses LendingClub loan data to explore borrower characteristics associated with loan defaults and identify patterns that can support credit risk monitoring.

Using Python for data preparation and exploratory analysis, and Power BI for interactive visualisation, the project examines loan performance across borrower and loan characteristics.

## Business Questions

- How does bad-loan rate vary across different loan grades?
- How are debt-to-income ratios and annual income associated with loan performance?
- Which loan characteristics are associated with higher observed default rates?
- How can borrower and loan segments support more informed portfolio monitoring?

## Tools & Technologies

- **Python:** Data cleaning, quality audits, exploratory data analysis and credit risk investigations.
- **Pandas:** Data manipulation and analysis.
- **Power BI:** Interactive dashboards, visual analysis and exploration.
- **GitHub:** Project documentation and version control.

## Data Preparation & Methodology

The analysis uses LendingClub loan data. Data preparation included cleaning, missingness assessment, financial data quality checks and exploratory analysis.

Loan outcomes were classified as follows:

- **Good loans (0):** Fully Paid.
- **Bad loans (1):** Charged Off and Default.
- **Unclassified:** Current, late, grace-period and other unresolved loan statuses were excluded from binary outcome analysis.

The classified population contains 1,306,387 loans.

## Key Findings

The overall bad-loan rate across classified loans was **20.07%**.

| Analysis | Key Finding |
|---|---:|
| Grade A bad-loan rate | 6.09% |
| Grade G bad-loan rate | 49.80% |
| DTI above 40 | 31.78% |
| DTI between 0 and 10 | 14.92% |
| 36-month loan bad-loan rate | 16.12% |
| 60-month loan bad-loan rate | 32.56% |
| Small business loan bad-loan rate | 29.91% |

The analysis shows substantial differences in observed bad-loan rates across loan grades, debt-to-income bands, loan terms and loan purposes.

## Business Recommendations

- Monitor higher-risk loan grades and borrower segments more closely.
- Consider debt-to-income levels as one component of borrower risk assessment.
- Compare loan performance across repayment terms when reviewing portfolio composition.
- Use segment-level monitoring to identify changes in portfolio risk over time.
- Combine multiple borrower characteristics rather than relying on a single risk indicator.

## Dashboard Preview

The Power BI dashboard provides an interactive view of loan performance, portfolio risk indicators, screening segments and factors associated with bad loans.

**Dashboard screenshot:** `dashboard/dashboard_screenshot.png`

**Power BI file:** `dashboard/credit_risk_dashboard.pbix`

## Limitations

- Unclassified loan statuses were excluded from binary good/bad outcome analysis.
- Missing, invalid and extreme values were assessed and documented rather than automatically treated as valid observations.
- The findings describe associations, not causal relationships.
- This project is exploratory and does not represent a validated predictive credit scoring model.
- The analysis is based on historical LendingClub data and should not be interpreted as a direct assessment of current lending conditions.

## Project Structure

```text
credit-risk-portfolio/
│
├── README.md
├── dashboard/
├── scripts/
├── reports/
└── .gitignore
```

## Author

**Timothy Madike**

BCom Quantitative Management student at UNISA | Aspiring Data Analyst

Interested in applying Python, SQL, Excel and Power BI to solve business problems and communicate data-driven insights.


