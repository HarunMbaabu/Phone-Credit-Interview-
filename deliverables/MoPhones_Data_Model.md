# MoPhones Reporting Data Model (ERD + dbt-style DAG)

This is a simple, production-oriented model for repeatable portfolio and customer-experience reporting.

## 1) ERD (Business Entities)

```mermaid
erDiagram
    DIM_CUSTOMERS ||--o{ FACT_ACCOUNTS : owns
    FACT_ACCOUNTS ||--o{ FACT_ACCOUNT_SNAPSHOTS : has_snapshot
    FACT_ACCOUNTS ||--o{ FACT_PAYMENTS : has_payment
    FACT_ACCOUNTS ||--o{ FACT_NPS_RESPONSES : receives_feedback
    DIM_DATES ||--o{ FACT_ACCOUNT_SNAPSHOTS : snapshot_date
    DIM_DATES ||--o{ FACT_PAYMENTS : payment_date
    DIM_DATES ||--o{ FACT_NPS_RESPONSES : survey_date
    DIM_PRODUCT ||--o{ FACT_ACCOUNTS : financed_device
    DIM_CHANNEL ||--o{ FACT_PAYMENTS : paid_via
    DIM_CHANNEL ||--o{ FACT_NPS_RESPONSES : survey_channel

    DIM_CUSTOMERS {
      string customer_id PK
      date dob
      string gender
      string region
      date first_seen_date
    }

    DIM_PRODUCT {
      string product_id PK
      string oem
      string model_name
      string price_tier
    }

    DIM_DATES {
      date date_key PK
      int year
      int month
      int quarter
      bool is_month_end
    }

    DIM_CHANNEL {
      string channel_id PK
      string channel_group
      string channel_name
    }

    FACT_ACCOUNTS {
      string account_id PK
      string customer_id FK
      string product_id FK
      date sale_date
      date maturity_date
      float financed_amount
      float deposit_amount
      float weekly_installment
      string origination_status
    }

    FACT_ACCOUNT_SNAPSHOTS {
      string account_snapshot_id PK
      string account_id FK
      date snapshot_date FK
      int days_past_due
      float total_paid_to_date
      float total_due_to_date
      float arrears_amount
      float balance_amount
      string account_status_l1
      string account_status_l2
    }

    FACT_PAYMENTS {
      string payment_id PK
      string account_id FK
      date payment_date FK
      string channel_id FK
      float payment_amount
      float adjustment_amount
      float prepayment_amount
      bool is_reversal
      string transaction_reference
    }

    FACT_NPS_RESPONSES {
      string nps_response_id PK
      string account_id FK
      date survey_date FK
      string channel_id FK
      int nps_score
      string service_satisfaction
      string device_satisfaction
      string free_text_reason
    }
```

## 2) dbt-style DAG (Transformation Layers)

```mermaid
flowchart LR
  subgraph staging
    stg_customers[stg_customers]
    stg_accounts[stg_accounts]
    stg_snapshots[stg_account_snapshots]
    stg_payments[stg_payments]
    stg_nps[stg_nps_responses]
    dim_dates[dim_dates]
    dim_channel[dim_channel]
    dim_product[dim_product]
  end

  subgraph marts
    fct_accounts[fct_accounts]
    fct_snapshots[fct_account_snapshots]
    fct_payments[fct_payments]
    fct_nps[fct_nps_responses]
  end

  subgraph semantic
    mart_portfolio[portfolio_health_mart]
    mart_collections[collections_effectiveness_mart]
    mart_cx[credit_x_nps_mart]
  end

  stg_customers --> fct_accounts
  stg_accounts --> fct_accounts
  dim_product --> fct_accounts

  stg_snapshots --> fct_snapshots
  fct_accounts --> fct_snapshots
  dim_dates --> fct_snapshots

  stg_payments --> fct_payments
  fct_accounts --> fct_payments
  dim_dates --> fct_payments
  dim_channel --> fct_payments

  stg_nps --> fct_nps
  fct_accounts --> fct_nps
  dim_dates --> fct_nps
  dim_channel --> fct_nps

  fct_snapshots --> mart_portfolio
  fct_payments --> mart_collections
  fct_snapshots --> mart_collections
  fct_nps --> mart_cx
  fct_snapshots --> mart_cx
```

## 3) Why this structure works

- `fact_account_snapshots` gives period-level risk reporting (PAR, DPD migration, default stock).
- `fact_payments` enables true collections analysis (cure curves, PTP behavior, channel effectiveness).
- `fact_nps_responses` allows credit performance to be measured against customer outcomes.
- Shared dimensions (`dates`, `channel`, `product`, `customers`) make reporting consistent and auditable.

## 4) Minimum governance rules

1. **Single account key standard** across source systems (`account_id`).
2. **Status dictionary** with controlled values + change log (`account_status_l1/l2`).
3. **Snapshot SLA** (e.g., monthly close + T+2 refresh) and data tests (nulls, uniqueness, referential integrity).
