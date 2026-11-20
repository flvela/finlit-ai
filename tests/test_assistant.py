"""Unit tests for FinLit AI assistant"""
import shutil

import pytest
from assistant import FinLitAssistant
from tools.articles import ARTICLE_COLLECTION_NAME, DEMO_ARTICLES, load_article_documents
from tools.config import Config
from tools.logger import get_logger
from tools.market_manager import MarketManager
from tools.portfolio_manager import PortfolioManager
from tools.vector_store import PERSIST_DIRECTORY, VectorStore

logger = get_logger(__name__)
# need to disable pylint redefined-outer-name in order to use pytest.fixture in this file
# pylint: disable=redefined-outer-name


@pytest.fixture
def vector_store() -> VectorStore:
  """function that creates vector store for fixture"""
  financial_articles = load_article_documents(DEMO_ARTICLES[0])
  financial_articles.extend(load_article_documents(DEMO_ARTICLES[1]))

  store = VectorStore(PERSIST_DIRECTORY, ARTICLE_COLLECTION_NAME, Config().get_langchain_embeddings())
  store.add_documents_if_empty(financial_articles)
  return store


@pytest.fixture
def assistant(vector_store) -> FinLitAssistant:
  """function to create the FinLitAssistant for testing"""
  portfolio_manager = PortfolioManager()
  return FinLitAssistant(portfolio_manager=portfolio_manager,
                         market_manager=MarketManager(),
                         vector_store=vector_store)


@pytest.fixture
def test_data():
  """creates test data for assistant"""
  return [
    # user finance faq agent test
    ("what is the difference between RSU and ESPP", ["ESPP", "RSU"]),
    ("how many IBM shares do I own", ["IBM"]),
    ("how are US financial markets moving today", ["S&P 500", "NASDAQ", "Dow Jones", "10-Year US Treasury", "Brent Crude"])
    ]


def shutdown(store: VectorStore):
  """Closes connection to vector store and cleans up data"""
  store.delete_collection()
  store.close()
  shutil.rmtree(PERSIST_DIRECTORY)


def test_ask(assistant, test_data, vector_store):
  """unit test for ask method of FinLitAssistant"""
  try:
    for (query, expected_answer_strings) in test_data:
      logger.info("query %s", query)
      logger.info("expected_answer %s", expected_answer_strings)
      answer = assistant.ask(query)
      assistant.reset()
      logger.info("FinLitAssistant answer %s", answer)
      assert answer is not None
      for expected_string in expected_answer_strings:
        assert expected_string.lower() in answer.lower()
  finally:
    # shutdown cleaning up data store connection if test passes or fails
    shutdown(vector_store)


def test_reset(assistant, vector_store):
  """unit test for reset method of FinLitAssistant"""
  thread_id = assistant.thread_id
  assistant.reset()

  try:
    assert thread_id != assistant.thread_id
  finally:
    # shutdown cleaning up data store connection if test passes or fails
    shutdown(vector_store)
