import logging
from typing import Annotated, Optional
import polars as pl

from langchain_core.messages import AnyMessage, AIMessage, ToolMessage, HumanMessage
from langgraph.constants import END
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, add_messages

from chatbots.get_preference import CustomerPreference, get_customer_preference, parse_customer_preference, \
    format_customer_preference
from chatbots.llm import build_llm
from chatbots.recommend import Recommendation, NO_RECOMMENDATION_MESSAGE, RECOMMENDATION_MESSAGE, retrieve_product_data
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
    recommended_product_data: pl.Dataframe


def manage_state(state: State) -> State:
    logger.debug("----------manage_state----------")
    """Helper function to manage the state of the graph during back-and-forth conversation"""
    if len(state["messages"]) <= 1:
        # empty input / only greeting message
        state["current_user_input"] = None
    elif len(state["messages"]) > 1:
        state["current_user_input"] = state["messages"][-1].content
    return state


def greeting_router(state: State) -> str:
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


def get_preference(state: State) -> State:
    logger.debug("----------get_preference----------")
    system_messages = get_customer_preference(state["messages"])
    response = llm_with_preference_tools.invoke(system_messages)
    state["messages"] = add_messages(state["messages"], [response])
    return state


def gather_preference(state: State):
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
    messages = state["messages"]
    if isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:
        logger.debug("ROUTER: gather_preference")
        return "gather_preference"
    elif not isinstance(messages[-1], HumanMessage):
        logger.debug("ROUTER: END")
        return END
    logger.debug("ROUTER: get_preference")
    return "get_preference"


def match_products(state: State):
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
    logger.debug("----------recommend----------")
    if "recommendation" not in state:
        # no recommendation
        state["messages"] = add_messages(state["messages"], AIMessage(content=NO_RECOMMENDATION_MESSAGE))
    # retrieve data for matched items
    state["recommended_product_data"] = retrieve_product_data(state["recommendation"].product_ids)
    state["messages"] = add_messages(state["messages"], AIMessage(content=RECOMMENDATION_MESSAGE.format()))
    return state


def shopping_buddy_graph_builder():
    builder = StateGraph(State)
    builder.add_node("get_preference", get_preference)
    builder.add_node("manage_state", manage_state)
    builder.add_node("greeting", lambda state: greeting(state))
    builder.add_node("gather_preference", gather_preference)
    builder.add_node("match_products", match_products)
    builder.add_node("recommend", recommend)

    builder.add_edge(START, "manage_state")
    builder.add_edge("manage_state", "greeting")
    builder.add_conditional_edges("greeting", greeting_router, [END, "get_preference"])
    builder.add_conditional_edges("get_preference", preference_router, ["gather_preference", "get_preference", END])
    builder.add_edge("gather_preference", "match_products")
    builder.add_edge("match_products", "recommend")
    builder.add_edge("recommend", END)
    return builder


def shopping_buddy_graph(builder):
    # adding thread-level persistence
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    return graph


# global object
llm = build_llm()
llm_with_preference_tools = llm.bind_tools([CustomerPreference])
builder = shopping_buddy_graph_builder()
graph = shopping_buddy_graph(builder)


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
