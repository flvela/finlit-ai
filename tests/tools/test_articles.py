"""tests for articles functions"""
import pytest

from tools.articles import (
  ARTICLE_CATEGORY,
  ARTICLE_NAME,
  ARTICLE_URL,
  load_article_documents
)

test_article_data = [
  ('data/aicpa_articles.json', 39),
  ('data/investopedia_articles.json', 36)
]


@pytest.mark.parametrize("file_path, num_articles", test_article_data)
def test_load_article_documents(file_path, num_articles):
  """unit test for load_article_documents"""
  documents = load_article_documents(file_path=file_path)
  assert len(documents) == num_articles
  for doc in documents:
    assert doc.metadata.get(ARTICLE_NAME) is not None, "Name metadata should not be None"
    assert doc.metadata.get(ARTICLE_CATEGORY) is not None, "Category metadata should not be None"
    assert doc.metadata.get(ARTICLE_URL) is not None, "URL metadata should not be None"
