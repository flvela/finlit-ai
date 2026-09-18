"""Unit tests for FinLit Graph"""
import shutil

from langgraph.graph import END, START

from agents import state
from agents.graph import (
  FINANCE_FAQ_NODE,
  FINANCE_FAQ_TOOL_NODE,
  ROUTER_NODE,
  build_graph
)

from tools.articles import ARTICLE_COLLECTION_NAME, load_article_documents
from tools.config import Config
from tools.logger import get_logger
from tools.vector_store import PERSIST_DIRECTORY, VectorStore

logger = get_logger(__name__)


def test_build_graph():
  """unit test for build_graph"""
  expected_nodes = [START, ROUTER_NODE, FINANCE_FAQ_NODE, FINANCE_FAQ_TOOL_NODE, END]
  expected_edges = {
    START: {
      ROUTER_NODE: (False, None)
    },
    ROUTER_NODE: {
      FINANCE_FAQ_NODE: (True, state.FINANCE_FAQ)
    },
    FINANCE_FAQ_NODE: {
      FINANCE_FAQ_TOOL_NODE: (True, state.FINANCE_FAQ_TOOLS),
      END: (True, state.GRAPH_END)
    },
    FINANCE_FAQ_TOOL_NODE: {
      FINANCE_FAQ_NODE: (False, None)
    }
  }

  articles = load_article_documents("data/aicpa_articles.json")
  articles.extend(load_article_documents("data/investopedia_articles.json"))
  vector_store = VectorStore(persist_directory=PERSIST_DIRECTORY, collection_name=ARTICLE_COLLECTION_NAME)
  article_collection = vector_store.get_create_collection(articles)
  config = Config()
  llm = config.get_llm()
  graph, context = build_graph(finance_article_collection=article_collection, llm=llm)
  try:
    graph_nodes = graph.get_graph().nodes.keys()
    assert list(graph.get_graph().nodes.keys()) == expected_nodes, f"Nodes {graph_nodes}, Expected Nodes {expected_nodes}"
    logger.info("graph edges %s", graph.get_graph().edges)
    for edge in graph.get_graph().edges:
      source_node = edge.source
      target_node = edge.target
      assert source_node in expected_edges
      assert target_node in expected_edges[source_node]
      attributes = expected_edges[source_node][target_node]
      assert attributes[0] == edge.conditional
      assert attributes[1] == edge.data
    assert context.article_collection == article_collection
    assert context.llm == llm
  finally:
    # cleanup vector store if test passes or fails
    vector_store.delete_collection()
    vector_store.close()
    shutil.rmtree(PERSIST_DIRECTORY)
