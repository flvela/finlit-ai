"""Unit tests for FinLit AI assistant"""
import pytest
from assistant import FinLitAssistant
from tools.articles import DEMO_ARTICLES, load_article_documents
from tools.logger import get_logger
from tools.portfolio_manager import PortfolioManager


test_data = [
  # user finance faq agent test
  ("what is the difference between RSU and ESPP", ["ESPP", "RSU"]),
  ("how many IBM shares do I own", ["IBM"])
]

logger = get_logger(__name__)


def init_assistant():
  """function to create the FinLitAssistant for testing"""
  financial_articles = load_article_documents(DEMO_ARTICLES[0])
  financial_articles.extend(load_article_documents(DEMO_ARTICLES[1]))
  portfolio_manager = PortfolioManager()
  return FinLitAssistant(financial_articles=financial_articles, portfolio_manager=portfolio_manager)


@pytest.mark.parametrize("query, expected_answer_strings", test_data)
def test_ask(query: str, expected_answer_strings):
  """unit test for ask method of FinLitAssistant"""
  assistant = init_assistant()
  answer = assistant.ask(query)
  logger.info("FinLitAssistant answer %s", answer)
  try:
    assert answer is not None
    for expected_string in expected_answer_strings:
      assert expected_string.lower() in answer.lower()
  finally:
    # shutdown cleaning up data store connection if test passes or fails
    assistant.shutdown()


def test_reset():
  """unit test for reset method of FinLitAssistant"""
  assistant = init_assistant()
  thread_id = assistant.thread_id
  assistant.reset()

  try:
    assert thread_id != assistant.thread_id
  finally:
    # shutdown cleaning up data store connection if test passes or fails
    assistant.shutdown()
