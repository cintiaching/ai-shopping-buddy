from dotenv import load_dotenv
import os
import polars as pl

load_dotenv()  # Load environment variables from .env file

# programmatically detect if running on databricks
IS_DATABRICKS: bool = "DATABRICKS_RUNTIME_VERSION" in os.environ
if IS_DATABRICKS:
    from databricks.sdk.runtime import spark

DATA_DIRECTORY = os.environ.get("DATA_DIRECTORY")


def read_dataset() -> pl.DataFrame:
    if IS_DATABRICKS:
        spark_df = spark.table("bright_data_best_buy_products_dataset.datasets.best_buy_products").toPandas()
        df = pl.from_pandas(spark_df)
    else:
        df = pl.read_csv(os.path.join(DATA_DIRECTORY, "best_buy_products.csv"), ignore_errors=True)
    return df
