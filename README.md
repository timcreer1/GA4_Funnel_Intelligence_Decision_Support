# GA4 Funnel Intelligence: From Raw Data to Decisions

Transforming the public Google Analytics 4 ecommerce BigQuery export into weekly funnel diagnostics, segment-level issue rankings, purchase propensity scores, intervention review groups, and a Power BI decision-support dashboard.

> Primary objective: convert raw, nested GA4 ecommerce event data into reproducible weekly decision outputs that help stakeholders identify which funnel issues should be reviewed first.

---

## Project Overview

This repository implements a reproducible, portfolio-style data science pipeline for ecommerce funnel intelligence:

* BigQuery access and GA4 schema exploration
* Flattened event-base creation from nested GA4 export fields
* Session, purchase label, funnel, item, order, and weekly fact table construction
* Funnel diagnostics across product view, cart, checkout, payment, and purchase stages
* Segment-step issue scoring using conversion gaps and estimated lost purchases
* Purchase propensity modelling with Logistic Regression and calibrated LightGBM
* Time-based train, validation, and test evaluation
* Power BI dashboard extracts and final stakeholder-facing recommendations

The project is built around the public Google Merchandise Store GA4 sample dataset and is designed to show the full movement from raw behavioural event data to practical decision support.

---

## Results (summary)

The final pipeline produced weekly dashboard-ready outputs from **360,129 sessions** and **4,848 purchase sessions** across the reporting window.

* Overall purchase rate: **1.35%**
* Latest selected reporting week: **Monday, 25 January 2021**
* Latest week sessions: **26,342**
* Latest week purchases: **310**
* Latest week purchase rate: **1.18%**
* Largest latest-week issue: **Google organic traffic: product view to cart drop-off**
* Estimated lost purchases for top issue: **58.1**
* Conversion gap for top issue: **5.9 percentage points**
* Final model: **calibrated LightGBM**
* Test PR-AUC: **0.8039**
* Top 100 precision: **85.00%**
* Top 100 lift: **72.23**

> In short: the project shows that raw GA4 event exports can be transformed into a structured decision pipeline that ranks funnel issues, identifies high-intent review groups, and communicates weekly priorities through a dashboard. The outputs are diagnostic and prioritisation-focused, not causal proof of recoverable purchases.

---

## ⚙️ Execution Environment (Important)

* Platform: final pipeline executed in **Google Colab**
* Data access: **Google BigQuery** public GA4 ecommerce export
* Dashboard: **Microsoft Power BI**
* Core environment: **Python 3.12.13**
* Main libraries: **pandas**, **scikit-learn**, **LightGBM**, **pandas-gbq**, **google-cloud-bigquery**, **matplotlib**, **seaborn**

BigQuery access still requires an authenticated Google Cloud session, even though the GA4 ecommerce sample dataset is public.

As a result:

* The repository is organised as executed notebooks plus lightweight saved artefacts
* Dashboard-ready CSV outputs are retained for review
* Data quality checks, run metadata, and SQL table definitions are retained for transparency
* Raw BigQuery extracts, Google credentials, and larger intermediate parquet files are intentionally not committed to GitHub

---

## Repository Structure

```text
GA4_Funnel_Intelligence_Decision_Support/
│
├── README.md
├── requirements.txt
├── environment.yml
├── .gitignore
│
├── notebooks/
│   ├── 00_setup_and_exploration.ipynb
│   ├── 01_events_base_and_gold_tables.ipynb
│   ├── 02_eda_funnel_segments_top_issues.ipynb
│   ├── 03_model_purchase_propensity.ipynb
│   └── 04_decision_summary.ipynb
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── bq_utils.py
│   ├── io_utils.py
│   ├── quality_checks.py
│   ├── issue_scoring.py
│   ├── model_utils.py
│   └── eval_utils.py
│
├── sql/
│   ├── events_base_create_table.sql
│   ├── sessions_create_table.sql
│   ├── funnel_steps_create_table.sql
│   ├── session_label_create_table.sql
│   ├── items_session_create_table.sql
│   ├── funnel_features_create_table.sql
│   ├── orders_create_table.sql
│   ├── fact_sessions_weekly_create_table.sql
│   └── fact_funnel_weekly_create_table.sql
│
├── outputs/
│   ├── data_quality/
│   │   ├── events_base_quality.json
│   │   ├── gold_tables_sanity.json
│   │   ├── notebook04_audit.json
│   │   ├── pre_purchase_feature_validation.json
│   │   ├── run_metadata.json
│   │   └── table_dictionary.csv
│   │
│   └── tables/
│       ├── combined_priority_candidates.csv
│       ├── fact_funnel_weekly.csv
│       ├── fact_sessions_weekly.csv
│       ├── funnel_weekly_rates.csv
│       ├── grouped_model_importance.csv
│       ├── model_comparison_metrics.csv
│       ├── ranking_cutoff_metrics.csv
│       ├── segment_step_metrics_weekly.csv
│       ├── top_issues_weekly.csv
│       └── weekly_decision_summary.csv
│
├── data/
│   └── README.md
│
└── reports/
    ├── Timothy_Creer_Final_Report1.pdf
    └── Timothy_Creer_GA4_Dashboard.pdf
```

---

## About Results and Outputs

To keep the repository lightweight and easy to review:

✅ **Committed to GitHub**

* `notebooks/*.ipynb` showing the full executed workflow
* `outputs/data_quality/*.json` containing data quality checks, leakage checks, run metadata, and final audit evidence
* `outputs/data_quality/table_dictionary.csv` summarising the main curated tables
* `outputs/tables/*.csv` containing Power BI-ready extracts and final decision outputs
* `sql/*.sql` containing the main BigQuery table creation scripts
* `reports/Timothy_Creer_GA4_Dashboard.pdf` showing the final Power BI dashboard
* `reports/Timothy_Creer_Final_Report1.pdf` providing academic context, methodology, results, discussion, and limitations

❌ **Not committed to GitHub**

* Raw BigQuery extracts
* Google Cloud credentials or service account keys
* `.env` files
* Large intermediate parquet files in `data/processed/`
* Full session-level scoring outputs such as `session_scores_all.parquet`
* Power BI local cache files
* Temporary notebook checkpoints

Everything excluded can be regenerated by running the notebooks in order.

---

## Data Source

Dataset: **Google Analytics 4 public ecommerce BigQuery export**

The dataset is an obfuscated sample of ecommerce behaviour from the Google Merchandise Store. It includes event-level records such as product views, add-to-cart actions, checkout steps, payment events, purchases, device attributes, geography, traffic source, nested event parameters, and repeated item fields.

The raw data is intentionally not committed to GitHub. The notebooks query:

```text
bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*
```

Expected access requirements:

* Google Cloud project
* BigQuery enabled
* Authenticated Google account in Colab
* Sufficient query quota or billing setup

---

## ⚙️ How to run

### Recommended notebook order

1. `00_setup_and_exploration.ipynb` → environment setup, BigQuery authentication, schema checks, event counts, and date range validation
2. `01_events_base_and_gold_tables.ipynb` → flattened event base, session tables, labels, funnel features, item features, order audit, weekly facts, and quality checks
3. `02_eda_funnel_segments_top_issues.ipynb` → funnel diagnostics, weekly rates, segment-step benchmarking, estimated lost purchases, and ranked top issues
4. `03_model_purchase_propensity.ipynb` → modelling dataset, time-based split, Logistic Regression, LightGBM, calibration, ranking metrics, and intervention candidates
5. `04_decision_summary.ipynb` → final decision summary, recommended focus table, dashboard extracts, weekly memo output, and run audit

### Minimal setup

1. Create the environment and install dependencies:

```bash
pip install -r requirements.txt
```

or:

```bash
conda env create -f environment.yml
conda activate ga4-funnel-intelligence
```

2. Authenticate Google Cloud in Colab:

```python
from google.colab import auth
auth.authenticate_user()
```

3. Set the Google Cloud project and output paths in the notebooks or `src/config.py`

4. Run the notebooks in order above

---

## Pipeline Stages

### 1. Raw GA4 event export

The source data is nested, event-level GA4 ecommerce data stored in BigQuery. Each row is an event, not a complete user journey.

### 2. Session and funnel preparation

Events are reshaped into session-level records. Funnel milestones are reconstructed using observed ecommerce events such as `view_item`, `add_to_cart`, `begin_checkout`, `add_payment_info`, and `purchase`.

### 3. Feature and weekly fact tables

Pre-purchase behavioural, item, funnel, device, geography, and traffic source features are created for modelling and dashboard reporting.

### 4. Segment issue detection

Segment-step combinations are compared against same-week site baselines. Issues are ranked using estimated lost purchases and conversion gap severity.

### 5. Purchase propensity model

A calibrated LightGBM model ranks sessions by purchase propensity using pre-purchase features. The model is evaluated using ranking-focused metrics rather than accuracy.

### 6. Decision outputs

The final layer combines funnel diagnostics, segment issues, model evidence, and review groups into Power BI-ready decision outputs.

---

## Methods Compared

### 1. Logistic Regression baseline

* Class-weighted baseline model
* Uses encoded tabular session features
* Included as a simple and interpretable reference point

### 2. LightGBM raw score

* Gradient-boosted tree model for tabular behavioural data
* Captures non-linear interactions between session behaviour, item intensity, funnel progression, and context
* Evaluated on the held-out test week

### 3. Calibrated LightGBM

* Final dashboard reporting model
* Uses sigmoid calibration to improve probability interpretation
* Preserves the LightGBM ranking while producing more usable purchase likelihood estimates

---

## Key Findings

* The largest funnel loss occurred between **product view** and **add to cart**
* The highest-priority latest-week issue was **Google organic traffic: product view to cart drop-off**
* The top issue had **58.1 estimated lost purchases** and a **5.9 percentage-point conversion gap**
* The calibrated LightGBM model achieved **85.00% top 100 precision** on the held-out test week
* The model produced a **72.23 lift** at the top 100 review cut-off
* The strongest intervention group was **late checkout recovery**, with 100 selected sessions and a median purchase likelihood of **71.55%**
* Browse and cart drop-off groups were more useful as diagnostic review groups than as high-probability recovery groups
* The dashboard translated technical outputs into weekly priorities for Product, UX, Ecommerce, Growth, and Analytics stakeholders

---

## Notes on Evaluation Design

* The model used a **time-based train, validation, and test split** rather than a random split
* Evaluation focused on **PR-AUC, precision, recall, lift, and Brier score**
* Accuracy was not used as the main metric because purchases were rare at approximately **1.35%** of sessions
* Pre-purchase leakage checks were used to confirm that post-purchase events, item records, and funnel steps were excluded from model features
* Estimated lost purchases were treated as prioritisation evidence, not as confirmed recoverable revenue
* The dashboard was designed to support stakeholder judgement, not replace controlled experimentation

This design was intended to keep the pipeline fair, interpretable, reproducible, and closer to a practical ecommerce analytics workflow.

---

## Limitations

* Results are based on one public GA4 ecommerce sample dataset
* The reporting period covers a seasonal ecommerce window from late 2020 to early 2021
* Model performance was evaluated on one held-out test week
* Estimated lost purchases are not actual lost purchases or guaranteed recoverable purchases
* The Power BI dashboard is based on static CSV extracts, not a live production data product
* No A/B testing or causal inference was performed
* The model is better suited to review-list prioritisation than automated real-time intervention

---

## Project provenance (academic context)

This repository is a portfolio-ready version of a University of Sydney postgraduate data science capstone project on GA4 ecommerce funnel analytics and decision support.

The original project aim was not just to report ecommerce metrics or train a model, but to connect the full workflow:

* raw BigQuery event data
* sessionisation and funnel reconstruction
* leakage-controlled feature engineering
* weekly segment issue ranking
* purchase propensity modelling
* intervention candidate generation
* Power BI dashboard communication

> In short: the repo is intended to show an end-to-end, research-style data science workflow where data engineering, diagnostics, modelling, and dashboard design are connected into one reproducible decision-support pipeline.

---

## Report

The final report is included in:

```text
reports/Timothy_Creer_Final_Report1.pdf
```

The Power BI dashboard export is included in:

```text
reports/Timothy_Creer_GA4_Dashboard.pdf
```

The report provides the full methodology, literature review, data preparation process, model evaluation, dashboard design, discussion, limitations, and references.

---

## References

* Google. (2024). BigQuery sample dataset for Google Analytics ecommerce web data.
* Google Analytics Help. BigQuery Export schema.
* Ke, G. et al. (2017). LightGBM: A highly efficient gradient boosting decision tree.
* Saito, T. and Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets.
* Kapoor, S. and Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science.
