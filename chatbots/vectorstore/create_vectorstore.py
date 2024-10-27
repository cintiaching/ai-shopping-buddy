# Databricks notebook source
# MAGIC %md
# MAGIC This script preprocesses the product data, vectorizes each product, and loads them into a vector database for use in vector searches during product recommendations.
# MAGIC
# MAGIC This notebook assumes that a Model Serving endpoint named databricks-bge-large-en exists.
# MAGIC To create that endpoint, see [documentation](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/create-query-vector-search#call-a-bge-embeddings-model-using-databricks-model-serving-notebook).

# COMMAND ----------

# MAGIC %pip install --upgrade --force-reinstall databricks-vectorsearch
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %pip install python-dotenv

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient

vsc = VectorSearchClient()

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient

vsc = VectorSearchClient()

# COMMAND ----------

catalog_name = "bright_data_best_buy_products_dataset"
schema_name = "datasets"
source_table_name = "best_buy_products"
source_table_fullname = f"{catalog_name}.{schema_name}.{source_table_name}"

# COMMAND ----------

# MAGIC %md
# MAGIC Create `text` column for embedding

# COMMAND ----------

from chatbots.vectorstore.vector_search import preprocess_product_data

data = spark.table(source_table_fullname)
data = preprocess_product_data(data)
display(data)

# COMMAND ----------

# save the data to catalog
processed_table_fullname = "main.default.best_buy_products_processed"
data.write.format("delta").option("delta.enableChangeDataFeed", "true").saveAsTable(processed_table_fullname)

# COMMAND ----------

# MAGIC %md
# MAGIC Create vector search endpoint

# COMMAND ----------

vector_search_endpoint_name = "vector-search-products-endpoint"

vsc.create_endpoint(
    name=vector_search_endpoint_name,
    endpoint_type="STANDARD"
)

endpoint = vsc.get_endpoint(
  name=vector_search_endpoint_name)
endpoint

# COMMAND ----------

# MAGIC %md 
# MAGIC Create vector index
# MAGIC

# COMMAND ----------

# Vector index
vs_index = "best_buy_products_index"
vs_index_fullname = f"main.default.{vs_index}"

embedding_model_endpoint = "databricks-bge-large-en"

# COMMAND ----------

index = vsc.create_delta_sync_index(
    endpoint_name=vector_search_endpoint_name,
    source_table_name=processed_table_fullname,
    index_name=vs_index_fullname,
    pipeline_type='TRIGGERED',
    primary_key="product_id",
    embedding_source_column="text",
    embedding_model_endpoint_name=embedding_model_endpoint
)
index.describe()

# COMMAND ----------

# MAGIC %md Get a vector index  
# MAGIC
# MAGIC Use `get_index()` to retrieve the vector index object using the vector index name.
# MAGIC
# MAGIC Use `describe()` on the index object to see a summary of the index's configuration information.

# COMMAND ----------

index = vsc.get_index(endpoint_name=vector_search_endpoint_name, index_name=vs_index_fullname)
index.describe()

# COMMAND ----------

# Wait for index to come online. Expect this command to take several minutes.
import time

while not index.describe().get('status').get('detailed_state').startswith('ONLINE'):
    print("Waiting for index to be ONLINE...")
    time.sleep(5)
print("Index is ONLINE")
index.describe()

# COMMAND ----------


