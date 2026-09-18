"""Unit tests for FinLit AI assistant"""
import pytest
from assistant import FinLitAssistant
from tools.articles import load_article_documents
from tools.logger import get_logger


test_data = [
  # user finance faq agent test
  ("what is the difference between RSU and ESPP",
   ["ESPP", "RSU"])
]

ARTICLE_FILE_1 = "data/aicpa_articles.json"
ARTICLE_FILE_2 = "data/investopedia_articles.json"

logger = get_logger(__name__)


@pytest.mark.parametrize("query, expected_answer_strings", test_data)
def test_ask(query: str, expected_answer_strings: list[str]):
  """unit test for ask method of SnackStackAssistant"""
  financial_articles = load_article_documents(ARTICLE_FILE_1)
  financial_articles.extend(load_article_documents(ARTICLE_FILE_2))
  assistant = FinLitAssistant(financial_articles=financial_articles)
  answer = assistant.ask(query)
  logger.info("FinLitAssistant answer %s", answer)

  try:
    assert answer is not None
    for expected_string in expected_answer_strings:
      assert expected_string.lower() in answer.lower()
  finally:
    # shutdown cleaning up data store connection if test passes or fails
    assistant.shutdown()
