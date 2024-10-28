from typing import List

from pydantic import BaseModel
import polars as pl

from chatbots.utils.environment import read_dataset

product_data = read_dataset()


class Recommendation(BaseModel):
    product_ids: List[int]
    score: List[float]


def retrieve_recommended_product_data(recommendation: Recommendation) -> pl.Dataframe:
    score_df = pl.DataFrame({
        "product_id": recommendation.product_ids,
        "score": recommendation.score
    })
    recommended_df = product_data.filter(pl.col("product_id").is_in(recommendation.product_ids))
    result_df = recommended_df.join(score_df, on="product_id", how="inner")
    return result_df


NO_RECOMMENDATION_MESSAGE = ""
RECOMMENDATION_MESSAGE = ""
