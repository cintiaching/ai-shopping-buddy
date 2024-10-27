from typing import List
from databricks.vector_search.client import VectorSearchClient

vsc = VectorSearchClient()
vector_search_endpoint_name = "vector-search-products-endpoint"
vs_index = "best_buy_products_index"
vs_index_fullname = f"main.default.{vs_index}"


def vector_search_product(query_text: str, columns: List[str], num_results: int=5):
    index = vsc.get_index(endpoint_name=vector_search_endpoint_name, index_name=vs_index_fullname)
    results = index.similarity_search(
        query_text=query_text,
        columns=columns,
        num_results=num_results,
    )
    return results
    
    