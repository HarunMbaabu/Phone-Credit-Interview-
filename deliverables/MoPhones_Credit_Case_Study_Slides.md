# MoPhones Credit Portfolio & CX Case Study
**Date:** 2026-04-19  
**Prepared for:** Chief Credit Officer & Executive Team

---

# 1) Business Context
- MoPhones finances smartphone purchases via installment plans.
- Growth depends on balancing credit access, collections efficiency, and customer trust.
- Core challenge: improve repayment outcomes without damaging customer experience.

---

# 2) Data Overview
- Credit snapshots: 5 cuts in 2025 (Jan, Mar, Jun, Sep, Dec).
- NPS survey file: 4,000+ responses, 3,413 unique loan IDs.
- Join coverage (latest snapshot): 3,026 matched accounts.

---

# 3) Assumptions
- Snapshot files represent point-in-time portfolio states.
- `ACCOUNT_STATUS_L2` used as canonical operational status.
- Missing income fields prevented direct `total_income/duration` computation.
- Installment burden proxy (`weekly_rate * 4.33`) used for income-band-like segmentation.

---

# 4) Portfolio Metrics (Selected)
1. PAR 30+
2. Default Rate
3. Repayment Rate
4. Average Days Past Due
5. Active vs Closed Ratio

**Rationale:** these directly connect to loss risk, cash realization, and operational posture.

---

# 5) Trend Results (2025)
- PAR30 increased from **35.4% → 39.0%**.
- Default rate increased from **28.1% → 33.4%**.
- Average DPD increased from **71.9 → 119.2 days**.
- Repayment rate remained broadly flat around **40–42%**.

**Interpretation:** risk is deteriorating faster than collections effectiveness.

---

# 6) Segment Insight (High Risk)
- Highest-risk latest segment: **55+ band**.
- Latest PAR30 for 55+: **43.2%**.
- Latest default for 55+: **40.2%**.

**Policy implication:** prioritize targeted controls for this segment while validating data quality first.

---

# 7) Credit × NPS Analysis
- Avg NPS (current, DPD<30): **7.01**
- Avg NPS (arrears, DPD≥30): **5.16**
- Avg NPS (default): **4.89**

**Finding:** deeper delinquency correlates with weaker customer sentiment.

---

# 8) Key Tension
- Harder collections can support short-term recovery.
- But customer friction (lock events, support pain) likely suppresses NPS and retention.

**Strategic trade-off:** optimize *both* cure rates and customer trust.

---

# 9) Recommendations
1. Risk-tiered collections strategy by DPD bucket.
2. Early-stage digital nudges before hard actions.
3. Assisted resolution path for recurring friction cases.
4. KPI redesign: track cure rate + NPS delta jointly.

---

# 10) Data Quality Issues
- Schema drift (`unnamed_col` in later files).
- Very high missingness in payment/adjustment fields.
- Implausible age distribution suggests demographic data reliability issue.
- No transaction-level payment fact table.

---

# 11) Data Foundation Improvements
1. Build `fact_payments` transaction table.
2. Standardize account-status dictionary and governance.
3. Capture behavioral telemetry (reminders, lock/unlock, support events).

---

# 12) Final Takeaway
MoPhones can materially improve portfolio resilience by combining:
- stronger early-risk controls,
- customer-sensitive collections design, and
- better data architecture for root-cause analytics.

**Bottom line:** sustainable credit performance requires risk discipline *and* experience discipline.
