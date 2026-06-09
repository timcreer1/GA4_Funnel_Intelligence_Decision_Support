# GA4 Funnel Intelligence: From Raw Data to Decisions

End-to-end GA4 ecommerce analytics pipeline that converts the public Google Analytics 4 BigQuery export into weekly funnel diagnostics, ranked segment issues, purchase propensity scores, intervention review groups, and a Power BI decision-support dashboard.

The project is designed as a portfolio-ready version of a University of Sydney data science capstone project. The main focus is not only model performance, but the full workflow from raw event data to practical stakeholder recommendations.

> Primary objective: transform nested GA4 ecommerce event data into reproducible, weekly decision outputs that help product, UX, ecommerce, growth, and analytics teams identify which funnel issues should be reviewed first.

---

## Project Overview

This repository implements a reproducible, notebook-led GA4 decision-support pipeline:

- BigQuery access and schema exploration for the public GA4 ecommerce export
- Event flattening and session-level table construction
- Funnel reconstruction across product view, cart, checkout, payment, and purchase stages
- Weekly funnel diagnostics and segment-step issue ranking
- Purchase propensity modelling using Logistic Regression and LightGBM
- Time-based train, validation, and test split to reduce leakage risk
- Calibrated LightGBM probabilities for dashboard interpretation
- Power BI dashboard extracts and final stakeholder-facing recommendations

The pipeline is structured around five notebooks. Each notebook produces intermediate or final artefacts that feed the next stage of the workflow.

---

## Results Summary

The final pipeline processed the public GA4 ecommerce sample into session-level and weekly decision outputs.

Key project results:

- Total sessions analysed: **360,129**
- Purchase sessions: **4,848**
- Overall purchase rate: **1.35%**
- Latest selected reporting week: **Monday, 25 January 2021**
- Latest week sessions: **26,342**
- Latest week purchases: **310**
- Latest week purchase rate: **1.18%**
- Highest-priority issue: **Google organic traffic: product view to cart drop-off**
- Estimated lost purchases for top issue: **58.1**
- Conversion gap for top issue: **5.9 percentage points**
- Final model: **calibrated LightGBM**
- Test PR-AUC: **0.8039**
- Top 100 precision: **85.00%**
- Top 100 lift: **72.23**

The findings should be interpreted as **prioritisation evidence**, not causal proof. The dashboard identifies what should be reviewed first, but any major website change should be validated through A/B testing or future monitoring before claiming conversion uplift.

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

## Data Source

The project uses the public Google Analytics 4 ecommerce sample export from the Google Merchandise Store.

Data source:

- Google Analytics 4 public ecommerce BigQuery export
- Source table pattern: `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
- Reporting window used in this project: **1 November 2020 to 31 January 2021**

The raw dataset is not committed to this repository. The project accesses the public dataset through BigQuery, which still requires:

- a Google Cloud project,
- an authenticated Google account,
- BigQuery access enabled,
- and sufficient BigQuery quota or billing setup.

---

## Notebook Workflow

Recommended notebook order:

1. **00_setup_and_exploration.ipynb**  
   Checks the environment, connects to BigQuery, inspects the raw GA4 schema, confirms event names, and validates that the selected date range contains the required ecommerce funnel events.

2. **01_events_base_and_gold_tables.ipynb**  
   Builds the main BigQuery and local gold tables, including flattened events, sessions, labels, funnel steps, funnel features, item-session summaries, orders, and weekly fact tables.

3. **02_eda_funnel_segments_top_issues.ipynb**  
   Performs funnel diagnostics, weekly conversion analysis, segment-step benchmarking, estimated lost purchase calculations, and top issue ranking.

4. **03_model_purchase_propensity.ipynb**  
   Builds the session-level modelling dataset, applies a time-based train/validation/test split, trains Logistic Regression and LightGBM models, calibrates LightGBM, evaluates ranking performance, and creates intervention candidates.

5. **04_decision_summary.ipynb**  
   Combines top issues, model evidence, intervention groups, and dashboard-ready recommendations into the final weekly decision summary and Power BI extracts.

---

## Outputs

The committed outputs are lightweight final artefacts used for review and dashboard reproduction.

Committed output groups:

- `outputs/data_quality/`  
  Data quality checks, row-count audits, leakage checks, run metadata, and table dictionary.

- `outputs/tables/`  
  Final CSV outputs used by Power BI, including funnel metrics, segment issue rankings, model metrics, review candidates, and decision summaries.

Not committed:

- raw BigQuery extracts,
- large parquet intermediates,
- full session scoring tables,
- local Google Drive caches,
- service account keys,
- `.env` files,
- or credential files.

All excluded artefacts can be regenerated by running the notebooks in order.

---

## Dashboard

The final dashboard was built in Power BI and exported as a PDF in the `reports/` folder.

Dashboard pages:

1. Executive Overview
2. Funnel Diagnostics
3. Segment and Top Issues
4. Model Performance
5. Intervention Review Groups
6. Methodology and Trust

The dashboard is designed to communicate weekly decision evidence, not to act as an automated production system. It summarises what to investigate first and includes interpretation notes to separate diagnostic evidence from causal claims.

---

## Modelling Approach

The purchase propensity model was framed as a ranking problem rather than a standard accuracy-focused classifier.

Main modelling choices:

- Target: `y_purchase`
- Feature set: 33 features before encoding
- Feature groups:
  - session behaviour
  - item intensity
  - funnel progression
  - device context
  - geography context
  - traffic source / medium
- Baseline model: class-weighted Logistic Regression
- Main model: LightGBM
- Final reporting model: calibrated LightGBM
- Evaluation split: time-based train, validation, and test
- Main metrics: PR-AUC, ROC-AUC, Brier score, precision, recall, and lift at review cut-offs

The final model was used to create review groups, not to automate customer-level decisions.

---

## Evaluation Design

The model was evaluated with a held-out test week rather than a random split. This was used because ecommerce behaviour varies across time due to seasonality, traffic mix, and campaign conditions.

Main ranking results for the calibrated LightGBM model:

| Review cut-off | Sessions reviewed | Precision | Recall | Lift |
|---|---:|---:|---:|---:|
| Top 100 | 100 | 85.00% | 27.42% | 72.23 |
| Top 250 | 250 | 81.60% | 65.81% | 69.34 |
| Top 1% | 264 | 81.06% | 69.03% | 68.88 |
| Top 2% | 527 | 58.82% | 100.00% | 49.98 |
| Top 5% | 1,318 | 23.52% | 100.00% | 19.99 |

These results show that the model was most useful for short, high-priority review lists rather than broad classification.

---

## How to Run

### 1. Create environment

Using pip:

```bash
pip install -r requirements.txt
```

Using conda:

```bash
conda env create -f environment.yml
conda activate ga4-funnel-intelligence
```

### 2. Authenticate Google Cloud in Colab

The notebooks were built around a Google Colab workflow. BigQuery access requires an authenticated Google Cloud session.

In Colab, authenticate before querying BigQuery:

```python
from google.colab import auth
auth.authenticate_user()
```

### 3. Set project details

Update the project constants in the notebooks or in `src/config.py`:

```python
BQ_PROJECT_ID = "your-google-cloud-project-id"
BQ_DATASET_ID = "ga4_capstone"
```

### 4. Run notebooks in order

Run:

```text
00_setup_and_exploration.ipynb
01_events_base_and_gold_tables.ipynb
02_eda_funnel_segments_top_issues.ipynb
03_model_purchase_propensity.ipynb
04_decision_summary.ipynb
```

The final CSV extracts will be written to the output folders and can be used in Power BI.

---

## Notes on `src/`

The notebooks are the primary executable workflow for this project. The `src/` folder contains reusable helper functions and configuration logic that mirrors repeated notebook operations, including BigQuery access, IO helpers, quality checks, issue scoring, model utilities, and evaluation metrics.

This keeps the repository aligned with the style of my other portfolio projects while preserving the original notebook-led academic workflow.

---

## Limitations

The project has several important limitations:

- The dataset is a public, historical GA4 sample rather than a current business dataset.
- The reporting window covers a seasonal ecommerce period.
- Model performance was evaluated on one final held-out week.
- Estimated lost purchases are prioritisation estimates, not confirmed recoverable purchases.
- The dashboard is based on static CSV exports rather than an automated live refresh.
- No A/B testing or causal inference was performed.

For production use, the next steps would be automated refresh, live monitoring, external validation, and controlled testing of recommended interventions.

---

## Project Provenance

This repository is a portfolio-ready version of a University of Sydney postgraduate data science capstone project.

The original project submission included:

- five Jupyter notebooks,
- a final written report,
- dashboard-ready CSV outputs,
- SQL table creation scripts,
- data quality audits,
- and a Power BI dashboard.

The public repository version is structured to make the pipeline easier to review while excluding raw data, credentials, and large intermediate artefacts.

---

## References

Google. (2024). BigQuery sample dataset for Google Analytics ecommerce web data. Google for Developers.

Google Analytics Help. BigQuery Export schema.

Ke, G. et al. (2017). LightGBM: A highly efficient gradient boosting decision tree.

Saito, T. and Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets.
