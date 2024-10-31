from typing import Optional, List

from langchain_core.messages import SystemMessage
from pydantic import BaseModel

template = """
Your job is to get 3 product categories based on the given product preference.

Given the recommended product data provide only three product category with most related accessories of recommended product preference.
- Product Category: Which type of electronic product are the related accessories belongs to?
"""


def get_related_product_preference(messages):
    return [SystemMessage(content=template)] + [f"Recommended Product: {messages}"]


class RelatedProductPreference(BaseModel):
    product_category_1: str
    product_category_2: str
    product_category_3: str


def parse_related_product_preference(args: dict) -> RelatedProductPreference:
    """Parse the given args from tool_calls and create a RelatedProductPreference instance."""
    related_product_preference_data = {
        "product_category_1": args["product_category_1"],
        "product_category_2": args["product_category_2"],
        "product_category_3": args["product_category_3"],
    }
    return RelatedProductPreference(**related_product_preference_data)


def format_related_product_preference(related_product_preference: RelatedProductPreference) -> str:
    """Format the given RelatedProductPreference into a string representation"""
    string = (f"Product Category 1: {related_product_preference.product_category_1}"
              f"Product Category 2: {related_product_preference.product_category_2} \n"
              f"Product Category 3: {related_product_preference.product_category_3}")
    return string

