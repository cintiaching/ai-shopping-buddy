from typing import List

from pydantic import BaseModel


class Recommendation(BaseModel):
    product_ids: List[str]
    score: List[float]
