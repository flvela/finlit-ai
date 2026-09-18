"""Common utils used for unit tests"""
from langgraph.runtime import Runtime

from agents.context_schema import ContextSchema
from tools.config import Config


def init_test_runtime():
  """test runtime initialization for LangGraph agents"""
  config = Config()
  context = ContextSchema(article_collection=None, llm=config.get_llm())
  return Runtime(context=context)
