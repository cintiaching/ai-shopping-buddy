from typing import Annotated, Optional

from langchain_core.messages import AnyMessage, AIMessage
from langgraph.constants import END
from typing_extensions import TypedDict

from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, add_messages

from chatbots.get_preference import CustomerPreference, get_customer_preference

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


def build_llm() -> ChatOllama:
    llm = ChatOllama(
        model="mistral",
        temperature=0,
    )
    return llm


def manage_state(state: State) -> State:
    print("----------manage_state----------")
    """Helper function to manage the state of the graph during back-and-forth conversation"""
    if len(state["messages"]) <= 1:
        # empty input / only greeting message
        state["current_user_input"] = None
    elif len(state["messages"]) > 1:
        state["current_user_input"] = state["messages"][-1].content
    return state


def greeting_router(state: State) -> str:
    if state["current_user_input"] is None:
        print("ROUTER: to the end")
        return END
    else:
        print("ROUTER: get_preference")
        return "get_preference"


def greeting(state: State) -> State:
    """Greeting message to the customer"""
    print("----------greeting----------")
    if state["messages"]:
        # already greeted the user
        state["messages"] = add_messages(state["messages"], [])
        return state
    # Return a greeting, since no message has been sent
    state["messages"] = add_messages(state["messages"], DEFAULT_GREETING)
    return state


def get_preference(state: State) -> State:
    print("----------get_preference----------")
    messages = get_customer_preference(state["messages"])
    state["messages"] = add_messages(state["messages"], messages)
    response = llm_with_preference_tools.invoke(messages)
    state["messages"] = add_messages(state["messages"], [response])
    return state


def print_buddy_response(input_message_list: list, config: dict):
    for event in graph.stream({"messages": input_message_list}, config=config):
        for value in event.values():
            print(value)
            if len(value["messages"]) > 0 and isinstance(value["messages"][-1], AIMessage):
                print("Shopping Buddy:", value["messages"][-1].content)


def shopping_buddy_langgraph():
    builder = StateGraph(State)
    builder.add_node("get_preference", get_preference)
    builder.add_node("manage_state", manage_state)
    builder.add_node("greeting", lambda state: greeting(state))

    builder.add_edge(START, "manage_state")
    builder.add_edge("manage_state", "greeting")
    builder.add_conditional_edges("greeting", greeting_router, [END, "get_preference"])
    builder.add_edge("get_preference", END)

    # adding thread-level persistence
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    return graph


if __name__ == "__main__":
    # allow interaction with chatbot
    llm = build_llm()
    llm_with_preference_tools = llm.bind_tools([CustomerPreference])
    graph = shopping_buddy_langgraph()

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
