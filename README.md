# MoPhones Credit Portfolio Health & Customer Experience Analysis

## 1) Objective
This project evaluates MoPhones' credit portfolio performance and the relationship between repayment risk and customer sentiment (NPS). The goal is to produce executive-ready insights and practical recommendations for credit policy and operational improvement.

## 2) Business Context
MoPhones provides smartphones on installment credit. This model expands access but introduces:
- **Default risk** (balances that are unlikely to be recovered),
- **Delinquency risk** (accounts rolling into arrears), and
- **Experience risk** (collections pressure reducing customer satisfaction and loyalty).

A sustainable strategy must balance portfolio stability, repayment performance, and customer trust.

## 3) Dataset Description
### Credit Portfolio Snapshots (CSV)
- `Credit Data - 01-01-2025.csv`
- `Credit Data - 30-03-2025.csv`
- `Credit Data - 30-06-2025.csv`
- `Credit Data - 30-09-2025.csv`
- `Credit Data - 30-12-2025.csv`

These files provide account-level states at different points in 2025 (DPD, balances, status, payments, etc.).

### Customer Experience Data (XLSX)
- `NPS Data (1).xlsx`

Contains loan-linked survey responses and 0–10 NPS scores.

## 4) Methodology
1. **Data Cleaning & Standardization**
   - Standardized schema issues (including blank column headers).
   - Handled missing values explicitly.
   - Enforced deterministic numeric parsing and snapshot date parsing.

2. **Feature Engineering**
   - Age band derivation (`18–25`, `26–35`, `36–45`, `46–55`, `55+`).
   - Income-band-style segmentation using an affordability proxy when direct income fields were unavailable.

3. **Portfolio Analysis**
   - Selected 5 high-impact metrics:
     - PAR 30+
     - Default Rate
     - Repayment Rate
     - Average DPD
     - Active vs Closed ratio
   - Trend analysis across all snapshots.
   - Segment review to identify a high-risk cohort.

4. **Credit × NPS Analysis**
   - Merged latest snapshot with NPS by loan ID.
   - Compared NPS across current vs arrears/default states.

5. **Data Quality Review**
   - Identified missingness, inconsistencies, and structural data gaps.
   - Proposed a future-state analytical data model.

## 5) Deliverables
- **Notebook:** `deliverables/MoPhones_Credit_Case_Study.ipynb`
- **Slide deck (12-slide structure):** `deliverables/MoPhones_Credit_Case_Study_Slides.md`
- **Analysis script:** `scripts/mophones_case_analysis.py`
- **Proposed reporting data model (ERD + DAG):** `deliverables/MoPhones_Data_Model.md`
- **Generated outputs:**
  - `deliverables/outputs/analysis_summary.json`
  - `deliverables/outputs/portfolio_metrics.csv`
  - `deliverables/outputs/age_segment_metrics.csv`

## 6) Key Insights
- Portfolio risk increased materially through 2025 (PAR30, default rate, and average DPD all rose).
- Repayment rate remained relatively flat, suggesting collections did not offset worsening risk migration.
- Joined NPS analysis showed significantly lower sentiment among arrears/default customers than current customers.
- A high-risk age segment was identified, but demographic distribution anomalies indicate caution before policy hard-coding.

## 7) Recommendations
1. Implement risk-tiered collections by DPD stage.
2. Introduce pre-delinquency and early-arrears treatment strategies to reduce roll rates.
3. Track customer impact in parallel with recovery outcomes (cure rate + NPS delta).
4. Prioritize data model upgrades (transaction-level payments, standardized statuses, behavioral events).

## 8) Assumptions
- Snapshot files represent point-in-time portfolio states.
- `ACCOUNT_STATUS_L2` is used as primary status layer for operational consistency.
- `total_income` and `duration` were not available in the provided credit files; therefore, direct `avg_monthly_income = total_income / duration` could not be computed.
- Affordability proxy (`weekly_rate * 4.33`) is used only for directional segmentation, not underwriting decisions.

## 9) Data Limitations
- Schema drift exists across snapshots (blank/unnamed columns).
- Some payment-related fields have high missingness.
- Demographic field behavior (age concentration) appears implausible and requires source validation.
- No transaction-level payment table limits causal analysis and behavior sequencing.

## 10) How to Run the Project
```bash
# From repository root
python scripts/mophones_case_analysis.py
```

This command generates reproducible artifacts in `deliverables/outputs/`.

Then open the notebook:
- `deliverables/MoPhones_Credit_Case_Study.ipynb`

## 11) Tools Used
- Python 3 (standard library only in this environment)
  - `csv`, `json`, `datetime`, `statistics`, `xml.etree.ElementTree`, `zipfile`, `pathlib`
- Jupyter Notebook format (`.ipynb`)
- Markdown-based executive slide deck format

---
If required, the slide deck can be converted to `.pptx` in a full environment with presentation tooling.
