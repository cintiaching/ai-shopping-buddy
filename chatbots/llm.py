from langchain_core.language_models import BaseChatModel
from langchain_databricks import ChatDatabricks

from chatbots.utils.environment import IS_DATABRICKS

if not IS_DATABRICKS:
    from langchain_ollama import ChatOllama


def build_llm(model_name="databricks-meta-llama-3-1-70b-instruct") -> BaseChatModel:
    if IS_DATABRICKS:
        llm = ChatDatabricks(endpoint=model_name)
    else:
        # for local development purpose
        llm = ChatOllama(
            model="mistral",
            temperature=0,
        )
    return llm
