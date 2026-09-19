"""Defines the FinLit AI assistant"""
import shutil
from typing import List
import uuid

from langchain_core.documents import Document
from langgraph.graph.state import Command, CompiledStateGraph

from agents.context_schema import ContextSchema
from agents.graph import build_graph
from agents.state import OUTPUT_FIELD
from tools.config import Config
from tools.articles import ARTICLE_COLLECTION_NAME
from tools.logger import get_logger
from tools.vector_store import PERSIST_DIRECTORY, VectorStore

logger = get_logger(__name__)

DEFAULT_ANSWER = "Sorry I could not process your request"


class FinLitAssistant:
  """Finlit AI assistant. Defines asks and other AI functions"""
  graph: CompiledStateGraph
  context: ContextSchema
  vector_store: VectorStore
  thread_id: str
  financial_articles: List[Document]
  is_interrupted: bool

  def __init__(self,
               financial_articles: List[Document],
               config: Config = Config()):
    """Constructor for FinLitAssistant"""

    self.financial_articles = financial_articles
    self.vector_store = VectorStore(persist_directory=PERSIST_DIRECTORY, collection_name=ARTICLE_COLLECTION_NAME)
    article_collection = self.vector_store.get_create_collection(financial_articles, config=config)
    self.graph, self.context = build_graph(finance_article_collection=article_collection, llm=config.get_llm())
    self.thread_id = str(uuid.uuid4())
    self.is_interrupted = False

  def reset(self):
    """resets the graph state and conversation"""
    self.thread_id = str(uuid.uuid4())

  def get_interrupt_value(self) -> bool:
    """if the graph was interrupted due to a HITL interrupt it
    returns the prompt value to user
    """
    config = {"configurable": {"thread_id": self.thread_id}}
    snapshot = self.graph.get_state(config)

    for interrupt in snapshot.interrupts:
      return interrupt.value
    return None

  def ask(self, query: str):
    """invokes finlit graph with user query.
    To start a new conversation use reset() method

    Args:
      query: the original user query to send to the graph
    """
    logger.info("Ask %s", query)
    if self.is_interrupted:
      graph_input = Command(resume=query)
      self.is_interrupted = False
      logger.info("Resuming graph with query %s", query)
    else:
      graph_input = {
        "user_input": query,
        "messages": [],
        "output": "",
        "route": ""}

    config = {"configurable": {"thread_id": self.thread_id}}
    result = self.graph.invoke(graph_input, config, context=self.context)
    logger.info("result %s", result)

    interrupt_value = self.get_interrupt_value()
    if interrupt_value is not None:
      self.is_interrupted = True
      return interrupt_value

    return result.get(OUTPUT_FIELD, DEFAULT_ANSWER)

  async def async_ask(self, query: str):
    """invokes snack stack graph using astream events with user query.
    To start a new conversation use reset() method

    Args:
      query: the original user query to send to the graph
    """
    interrupted_value = self.get_interrupt_value()
    logger.info("Async Ask %s interrupted_value %s", query, interrupted_value)

    if interrupted_value is not None:
      graph_input = Command(resume=query)
      self.is_interrupted = False
      logger.info("Resuming graph with query %s", query)
    else:
      graph_input = {
          "user_input": query,
          "messages": [],
          "output": "",
          "route": ""}

    config = {"configurable": {"thread_id": self.thread_id}}
    return self.graph.astream_events(graph_input, config, context=self.context, version="v2")

  def get_last_message(self):
    """gets the last message from the graph to the user"""
    config = {"configurable": {"thread_id": self.thread_id}}
    snapshot = self.graph.get_state(config)
    return snapshot.values.get(OUTPUT_FIELD, DEFAULT_ANSWER)

  def shutdown(self):
    """Closes connection to vector store and cleans up data"""
    self.vector_store.delete_collection()
    self.vector_store.close()
    shutil.rmtree(PERSIST_DIRECTORY)
