from typing import List, Tuple, Optional
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
    

def process_search_result(search_results) -> Tuple[Optional[List[str]], Optional[List[float]]]:
    """Process search result from similarity_search, return only product ids and similarity scores"""
    search_results = search_results["result"]
    result_length = search_results["row_count"]
    if result_length == 0:
        return None, None
    result_ids = [result[0] for result in search_results["data_array"]]
    result_similarity = [result[-1] for result in search_results["data_array"]]
    return result_ids, result_similarity
