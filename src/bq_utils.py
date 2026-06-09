#------------------------------------------------------------------------------
# BigQuery helper functions
#------------------------------------------------------------------------------
from pathlib import Path

import pandas as pd
import pandas_gbq

try:
    from google.cloud import bigquery
except Exception:
    bigquery = None

from .config import BQ_PROJECT_ID, BQ_DATASET_ID, BQ_LOCATION, SQL_DIR

#------------------------------------------------------------------------------
# Run a BigQuery query and return a dataframe
#------------------------------------------------------------------------------
def run_bq(sql, project_id=BQ_PROJECT_ID, location=BQ_LOCATION):
    return pandas_gbq.read_gbq(sql, project_id=project_id, location=location, progress_bar_type=None)

#------------------------------------------------------------------------------
# Create the BigQuery dataset when it does not exist
#------------------------------------------------------------------------------
def ensure_dataset(project_id=BQ_PROJECT_ID, dataset_id=BQ_DATASET_ID, location=BQ_LOCATION):
    if bigquery is None:
        raise ImportError("google-cloud-bigquery is required for ensure_dataset().")
    client = bigquery.Client(project=project_id)
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset_ref.location = location
    client.create_dataset(dataset_ref, exists_ok=True)
    return f"{project_id}.{dataset_id}"

#------------------------------------------------------------------------------
# Save a SQL script and run it through BigQuery
#------------------------------------------------------------------------------
def save_sql_and_run(file_name, sql_text, sql_dir=SQL_DIR, project_id=BQ_PROJECT_ID, location=BQ_LOCATION):
    if bigquery is None:
        raise ImportError("google-cloud-bigquery is required for save_sql_and_run().")
    sql_dir = Path(sql_dir)
    sql_dir.mkdir(parents=True, exist_ok=True)
    sql_path = sql_dir / file_name
    sql_path.write_text(sql_text, encoding="utf-8")

    client = bigquery.Client(project=project_id, location=location)
    job = client.query(sql_text)
    job.result()
    print("Saved SQL ->", sql_path)
    return sql_path

#------------------------------------------------------------------------------
# Export a query to CSV and/or parquet
#------------------------------------------------------------------------------
def export_query(sql, csv_path=None, parquet_path=None, date_cols=None, datetime_cols=None, string_cols=None,
                 project_id=BQ_PROJECT_ID, location=BQ_LOCATION):
    df = run_bq(sql, project_id=project_id, location=location)

    # Convert selected columns into safer local formats
    for col in date_cols or []:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.date
    for col in datetime_cols or []:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    for col in string_cols or []:
        if col in df.columns:
            df[col] = df[col].astype("string")

    # Save outputs when paths are provided
    if csv_path is not None:
        csv_path = Path(csv_path)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path, index=False)
        print("Saved CSV ->", csv_path)

    if parquet_path is not None:
        parquet_path = Path(parquet_path)
        parquet_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(parquet_path, index=False)
        print("Saved parquet ->", parquet_path)

    return df

#------------------------------------------------------------------------------
# Preview a BigQuery table
#------------------------------------------------------------------------------
def preview_table(table_id, limit=5, project_id=BQ_PROJECT_ID, location=BQ_LOCATION):
    sql = f"SELECT * FROM `{table_id}` LIMIT {int(limit)}"
    return run_bq(sql, project_id=project_id, location=location)

#------------------------------------------------------------------------------
# Return a simple row-count check for a table
#------------------------------------------------------------------------------
def get_table_row_count(table_id, project_id=BQ_PROJECT_ID, location=BQ_LOCATION):
    sql = f"SELECT COUNT(*) AS row_count FROM `{table_id}`"
    result = run_bq(sql, project_id=project_id, location=location)
    return int(result["row_count"].iloc[0])
