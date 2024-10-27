import pyspark.sql.functions as f
from pyspark.sql import DataFrame


def preprocess_product_data(data: DataFrame) -> DataFrame:
    """Preprocess the Best Buy product data by adding a text column to the dataframe"""
    data = data.withColumn(
        "text",
        f.format_string(
            "Product Name: %s \n Product Category: %s \n Features Summary: %s \n"
            "Features: %s \n Product Specifications: %s \n Final Price: %s",
            f.col("title"),
            f.col("root_category"),
            f.col("features_summary"),
            f.col("features"),
            f.col("product_specifications"),
            f.col("final_price"),
        )
    )
    return data
    