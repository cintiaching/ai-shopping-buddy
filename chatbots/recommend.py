from typing import List

from pydantic import BaseModel
import polars as pl

from chatbots.utils.environment import read_dataset

NO_RECOMMENDATION_MESSAGE = "I'm sorry, but I couldn't find any recommendations based on your preferences."
product_data = read_dataset()


class Recommendation(BaseModel):
    product_ids: List[int]
    score: List[float]


def retrieve_recommended_product_data(recommendation: Recommendation) -> dict:
    """Get product attributes from Recommendation object"""
    score_df = pl.DataFrame({
        "product_id": recommendation.product_ids,
        "score": recommendation.score
    })
    recommended_df = product_data.filter(pl.col("product_id").is_in(recommendation.product_ids))
    result_df = recommended_df.join(score_df, on="product_id", how="inner").sort("score", descending=True)
    return result_df.to_dict(as_series=False)


def format_recommendation_message(recommended_product_data: dict) -> str:
    """Format final recommendation message"""
    msg = "Here are the recommended products based on your preferences: \n"
    for title, price in zip(recommended_product_data["title"], recommended_product_data["final_price"]):
        msg += f"""{title} - {price}\n"""
    return msg


def format_relate_product_message(related_product_data: dict) -> str:
    msg = "Here are the related products that you may also like: \n"
    for title, price in zip(related_product_data["title"], related_product_data["final_price"]):
        msg += f"""{title} - {price}\n"""
    return msg
