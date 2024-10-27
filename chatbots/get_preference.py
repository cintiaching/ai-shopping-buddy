from typing import Optional, List

from langchain_core.messages import SystemMessage
from pydantic import BaseModel

template = """Your job is to get product preference from a customer about what type of electronic product they want to buy.

You should get the following information from them:

- Product Category: Which type of electronic product are they interested in?
- Brand Preferences: Do they have any preferred brands?
- Budget Range: What is their budget for the purchase?
- Features: Are there specific features they are looking for?

If you are not able to discern this info, ask them to clarify! Do not attempt to wildly guess.
Put None if customer did not give the desired information after asking. 
After you are able to discern all the information, call the relevant tool."""


def get_customer_preference(messages):
    return [SystemMessage(content=template)] + messages


class CustomerPreference(BaseModel):
    product_category: str
    brand: Optional[List[str]]
    budget: Optional[List[str]]
    features: Optional[List[str]]
