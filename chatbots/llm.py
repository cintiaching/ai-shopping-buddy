from langchain_core.language_models import BaseChatModel
from langchain_databricks import ChatDatabricks

from chatbots.utils.environment import IS_DATABRICKS

if not IS_DATABRICKS:
    from langchain_ollama import ChatOllama


def build_llm(model_name="databricks-dbrx-instruct") -> BaseChatModel:
    llm = ChatDatabricks(
        target_uri="databricks",
        endpoint=model_name,
        temperature=0,
    )
    return llm
