from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.constants import END
from typing_extensions import TypedDict

from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, add_messages


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def build_llm() -> ChatOllama:
    llm = ChatOllama(
        model="mistral",
        temperature=0,
    )
    return llm


def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def print_buddy_response(user_input: str, config: dict):
    for event in graph.stream({"messages": [("user", user_input)]}, config=config):
        for value in event.values():
            print("Shopping Buddy:", value["messages"][-1].content)


llm = build_llm()

builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# adding thread-level persistence
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)


thread_id = 1
print(f"""Starting thread {thread_id}, type "quit", "exit" or "q" to exit chatbot. 
Type "clear" to clear memory and start a new thread.""")
while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Shopping Buddy: Goodbye!")
        break
    if user_input.lower() in ["clear"]:
        thread_id += 1
    else:
        config = {"configurable": {"thread_id": thread_id}}
        print_buddy_response(user_input, config)
