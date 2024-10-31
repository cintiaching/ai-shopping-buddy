import logging
from typing import Annotated, Optional

from langchain_core.messages import AnyMessage, AIMessage, ToolMessage, HumanMessage
from langgraph.constants import END
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, add_messages

from chatbots.get_related_product import RelatedProductPreference, get_related_product_preference, \
    parse_related_product_preference, format_related_product_preference
from chatbots.customer_preference import (
    CustomerPreference,
    get_customer_preference_prompt,
    parse_customer_preference,
    format_customer_preference,
)
from chatbots.llm import build_llm
from chatbots.recommend import (
    Recommendation,
    NO_RECOMMENDATION_MESSAGE,
    retrieve_recommended_product_data,
    format_recommendation_message,
    format_relate_product_message,
)
from chatbots.vectorstore.vector_search import vector_search_product, process_search_result

logger = logging.getLogger("chatbots")

DEFAULT_GREETING = AIMessage(content="""👋 Hello and Welcome!

I’m your AI shopping assistant, here to help you find exactly what you’re looking for!
To get started, I’d love to know a bit more about your preferences.

1. What type of products are you interested in? (e.g., Home Appliances, Computers & Tablets, Cell Phones)
2. Do you have any specific brands in mind?
3. What’s your budget range?
4. Are there any features or styles you particularly like?
Feel free to share as much or as little as you like, and I’ll do my best to recommend the perfect products just for you! 🛍️✨
""")


class State(TypedDict):
    current_user_input: Optional[str]
    messages: Annotated[list[AnyMessage], add_messages]

    customer_preference: CustomerPreference
    recommendation: Recommendation
    recommended_product_data: dict

    related_product_preference: RelatedProductPreference
    related_product_recommendation: Recommendation
    related_product_data: dict


def manage_state(state: State) -> State:
    """Helper function to manage the state of the graph during back-and-forth conversation"""
    logger.debug("----------manage_state----------")
    if len(state["messages"]) <= 1:
        # empty input / only greeting message
        state["current_user_input"] = None
    elif len(state["messages"]) > 1:
        state["current_user_input"] = state["messages"][-1].content
    return state


def greeting_router(state: State) -> str:
    """Conditional edge function after greeting node"""
    if state["current_user_input"] is None:
        logger.debug("ROUTER: to the end")
        return END
    else:
        logger.debug("ROUTER: get_preference")
        return "get_preference"


def greeting(state: State) -> State:
    """Greeting message to the customer"""
    logger.debug("----------greeting----------")
    if state["messages"]:
        # already greeted the user
        state["messages"] = add_messages(state["messages"], [])
        return state
    # Return a greeting, since no message has been sent
    state["messages"] = add_messages(state["messages"], DEFAULT_GREETING)
    return state


def gather_preference(state: State) -> State:
    """Get user preference"""
    logger.debug("----------get_preference----------")
    system_messages = get_customer_preference_prompt(state["messages"])
    response = llm_with_preference_tools.invoke(system_messages)
    state["messages"] = add_messages(state["messages"], [response])
    return state


def parse_preference(state: State):
    """Parse user preference"""
    logger.debug("----------gather_preference----------")
    state["customer_preference"] = parse_customer_preference(state["messages"][-1].tool_calls[0]["args"])
    state["messages"] = add_messages(state["messages"], [
        ToolMessage(
            content="Customer preferences gathered",
            tool_call_id=state["messages"][-1].tool_calls[0]["id"],
        )
    ])
    return state


def preference_router(state):
    """Conditional edge for whether to continue to ask for user preference, move on to parsing or END"""
    messages = state["messages"]
    if isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:
        logger.debug("ROUTER: parse_preference")
        return "parse_preference"
    elif not isinstance(messages[-1], HumanMessage):
        logger.debug("ROUTER: END")
        return END
    logger.debug("ROUTER: gather_preference")
    return "gather_preference"


def match_products(state: State):
    """Match products to user preference"""
    logger.debug("----------match_product----------")
    # format customer_preference
    query_text = format_customer_preference(state["customer_preference"])
    # vector search
    search_result = vector_search_product(query_text, columns=["product_id", "title", "text"])
    product_ids, similarity = process_search_result(search_result)
    if len(product_ids):
        state["recommendation"] = Recommendation(product_ids=product_ids, score=similarity)
        logger.debug(f"recommendations: {state['recommendation']}")
    return state


def recommend(state: State):
    """Display recommendations"""
    logger.debug("----------recommend----------")
    if "recommendation" not in state:
        # no recommendation
        state["messages"] = add_messages(state["messages"], AIMessage(content=NO_RECOMMENDATION_MESSAGE))
    # retrieve data for matched items
    state["recommended_product_data"] = retrieve_recommended_product_data(state["recommendation"])
    state["messages"] = add_messages(state["messages"],
                                     AIMessage(
                                         content=format_recommendation_message(state["recommended_product_data"])))
    return state


def related_router(state: State) -> str:
    if state["recommended_product_data"] is None:
        logger.debug("ROUTER: to the end")
        return END
    else:
        logger.debug("ROUTER: find_related_products")
        return "find_related_products"


def find_related_products(state: State) -> State:
    logger.debug("----------find_related_products----------")
    system_messages = get_related_product_preference(state["customer_preference"])
    response = llm_with_product_tools.invoke(system_messages)
    state["messages"] = add_messages(state["messages"], [response])
    state["related_product_preference"] = parse_related_product_preference(response.tool_calls[0]["args"])
    state["messages"] = add_messages(state["messages"], [
        ToolMessage(
            content="Related Product Preference gathered",
            tool_call_id=state["messages"][-1].tool_calls[0]["id"],
        )
    ])
    related_product_preference = format_related_product_preference(state["related_product_preference"])
    # vector search
    product_id_list = []
    similarity_list = []
    for product in related_product_preference:
        search_result = vector_search_product(product, columns=["product_id", "title", "text"], num_results=5)
        product_ids, similarities = process_search_result(search_result)
        for product_id, similarity in zip(product_ids, similarities):
            if product_id in product_id_list:
                continue
            else:
                product_id_list.append(product_id)
                similarity_list.append(similarity)
                break
    if len(product_ids):
        state["related_product_recommendation"] = Recommendation(product_ids=product_id_list, score=similarity_list)
        logger.debug(f"related product recommendations: {state['related_product_recommendation']}")

    return state

def recommend_related_product(state: State) -> State:
    logger.debug("----------recommend_related_product----------")
    if "related_product_recommendation" in state:

        state["related_product_data"] = retrieve_recommended_product_data(state["related_product_recommendation"])
        state["messages"] = add_messages(state["messages"],
                                        AIMessage(
                                            content=format_relate_product_message(state["related_product_data"])))
    return state


def shopping_buddy_graph_builder():
    builder = StateGraph(State)
    builder.add_node("gather_preference", gather_preference)
    builder.add_node("manage_state", manage_state)
    builder.add_node("greeting", lambda state: greeting(state))
    builder.add_node("parse_preference", parse_preference)
    builder.add_node("match_products", match_products)
    builder.add_node("recommend", recommend)
    builder.add_node("find_related_products", find_related_products)
    builder.add_node("recommend_related_product", recommend_related_product)

    builder.add_edge(START, "manage_state")
    builder.add_edge("manage_state", "greeting")
    builder.add_conditional_edges("greeting", greeting_router, [END, "gather_preference"])
    builder.add_conditional_edges("gather_preference", preference_router,
                                  ["parse_preference", "gather_preference", END])
    builder.add_edge("parse_preference", "match_products")
    builder.add_edge("match_products", "recommend")
    builder.add_conditional_edges("recommend", related_router, ["find_related_products", END])
    builder.add_edge("find_related_products", "recommend_related_product")
    builder.add_edge("recommend_related_product", END)
    return builder


def shopping_buddy_graph(builder):
    # adding thread-level persistence
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    return graph


# global object
llm = build_llm()
llm_with_preference_tools = llm.bind_tools([CustomerPreference])
llm_with_product_tools = llm.bind_tools([RelatedProductPreference])
builder = shopping_buddy_graph_builder()
graph = shopping_buddy_graph(builder)


# for frontend
def shopping_buddy(user_message: str, thread_id: int = 1) -> str:
    """
    Generator function that yields chatbot response based on user message.
    Default first output is greeting message
    :param user_message: str
    :param thread_id: int (default 1), update thread_id to clear memory
    :yield: (str) chatbot response
    """
    config = {"configurable": {"thread_id": thread_id}}

    # empty input for involving greeting
    empty_input = []
    for event in graph.stream({"messages": empty_input}, config=config):
        for value in event.values():
            if len(value["messages"]) > 0 and isinstance(value["messages"][-1], AIMessage):
                yield value["messages"][-1].content

    for event in graph.stream({"messages": [("user", user_message)]}, config=config):
        for value in event.values():
            if len(value["messages"]) > 0 and isinstance(value["messages"][-1], AIMessage):
                yield value["messages"][-1].content


# for development
def print_buddy_response(input_message_list: list, config: dict):
    for event in graph.stream({"messages": input_message_list}, config=config):
        for value in event.values():
            logger.debug(value)
            if len(value["messages"]) > 0 and isinstance(value["messages"][-1], AIMessage):
                print("Shopping Buddy:", value["messages"][-1].content)
                if value["messages"][-1].tool_calls:
                    logger.debug(f"TOOL_CALLS: {value['messages'][-1].tool_calls}")


def main():
    # allow interaction with chatbot

    thread_id = 1
    print(f"""Starting thread {thread_id}, type "quit", "exit" or "q" to exit chatbot.
Type "clear" to clear memory and start a new thread.""")
    config = {"configurable": {"thread_id": thread_id}}

    # empty input for involving greeting
    first_input = []
    print_buddy_response(first_input, config)

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Shopping Buddy: Goodbye!")
            break
        if user_input.lower() in ["clear"]:
            thread_id += 1
        else:
            input_msg_list = [("user", user_input)]
            print_buddy_response(input_msg_list, config)
