from langchain_ollama import ChatOllama
from chatbots.shopping_buddy import build_llm


def test_build_llm():
    llm = build_llm()
    assert isinstance(llm, ChatOllama)
