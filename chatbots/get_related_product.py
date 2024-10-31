from langchain_core.messages import SystemMessage
from pydantic import BaseModel

template = """
Task: Provide Product Categories Based on Customer Preferences

Your objective is to extract three product categories based on the provided product preference data.

Instructions:

Review the recommended product preference carefully.
Identify the three most relevant product categories.
Include the associated accessories that align with product preference category.
Output Format:

Product Category: Specify the type of electronic product the related accessories belong to.
Please ensure your categories are well-defined and directly related to the preferences given.
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


def format_related_product_preference(related_product_preference: RelatedProductPreference) -> list:
    """Format the given RelatedProductPreference into a list representation"""
    preference_list = [f"Product Category 1: {related_product_preference.product_category_1}",
                       f"Product Category 2: {related_product_preference.product_category_2}",
                       f"Product Category 3: {related_product_preference.product_category_3}"]
    return preference_list
