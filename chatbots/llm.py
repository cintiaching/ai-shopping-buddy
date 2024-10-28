from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_databricks import ChatDatabricks

from chatbots.utils.environment import IS_DATABRICKS


def build_llm(model_name="databricks-dbrx-instruct") -> BaseChatModel:
    if IS_DATABRICKS:
        llm = ChatDatabricks(endpoint=model_name)
    else:
        # for local development purpose
        llm = ChatOllama(
            model="mistral",
            temperature=0,
        )
    return llm
