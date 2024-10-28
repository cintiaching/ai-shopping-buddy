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
After you are able to discern all the information, 
give the customer a summary of the gathered preference and call the get_preference tool."""


def get_customer_preference(messages):
    return [SystemMessage(content=template)] + messages


class CustomerPreference(BaseModel):
    product_category: str
    brand: Optional[List[str]]
    budget: Optional[List[str]]
    features: Optional[List[str]]


def parse_customer_preference(args: dict) -> CustomerPreference:
    """Parse the given args from tool_calls and create a CustomerPreference instance."""
    customer_preference_data = {
        "product_category": args["product_category"],
        "brand": [args["brand"]] if args["brand"] != "None" else None,
        "budget": [args["budget"]] if args["brand"] != "None" else None,
        "features": [args["features"]] if args["brand"] != "None" else None,
    }
    return CustomerPreference(**customer_preference_data)


def format_customer_preference(customer_preference: CustomerPreference) -> str:
    """Format the given CustomerPreference into a string representation"""
    string = (f"Product Brand: {", ".join(customer_preference.brand)}"
              f"Product Category: {customer_preference.product_category} \n"
              f"Features: {", ".join(customer_preference.features)}"
              f"Final Price: {", ".join(customer_preference.budget)}")
    return string
