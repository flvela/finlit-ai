"""Defines the FinLit AI assistant"""
import uuid

from langgraph.graph.state import Command, CompiledStateGraph

from agents.graph import build_graph
from agents.state import OUTPUT_FIELD
from tools.config import Config
from tools.logger import get_logger
from tools.market_manager import MarketManager
from tools.portfolio_manager import PortfolioManager
from tools.vector_store import VectorStore

logger = get_logger(__name__)

DEFAULT_ANSWER = "Sorry I could not process your request"


class FinLitAssistant:
  """Finlit AI assistant. Defines asks and other AI functions"""
  graph: CompiledStateGraph
  thread_id: str
  is_interrupted: bool

  def __init__(self,
               portfolio_manager: PortfolioManager,
               market_manager: MarketManager,
               vector_store: VectorStore,
               config: Config = Config()):
    """Constructor for FinLitAssistant"""
    self.graph, self.context = build_graph(finance_article_collection=vector_store, llm=config.get_llm(),
                                           portfolio_manager=portfolio_manager, market_manager=market_manager)
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
