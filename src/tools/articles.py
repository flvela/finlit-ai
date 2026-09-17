"""tools to load and search financial articles"""
import json
import logging
from typing import List

from langchain_core.documents import Document

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

#Article constants
ARTICLE_NAME = "name"
ARTICLE_CATEGORY = "category"
ARTICLE_CONTENT = "content"
ARTICLE_URL = "url"
ARTICLE_COLLECTION_NAME = "financial_literarcy_articles"


def load_article_documents(file_path: str) -> List[Document]:
  """
  Load article documents from a JSON file

  Args:
    file_path (str): Path to the JSON file containing article documents.
  Returns:
    list: A list of article documents.
  """
  with open(file_path, 'r', encoding='utf-8') as file:
    items = json.load(file)
    logger.info("loaded %d articles from %s file", len(items), file_path)

    return load_article_documents_from_json(items)

def load_article_documents_from_json(json_documents: list[dict]):
  """
    Load article documents from a JSON list.

  Args:
    json_documents (list[dict]): The document list containing article documents.
  Returns:
    list: A list of LangChain article documents
  """
  documents = []
  for item in json_documents:
    doc = Document(page_content=item[ARTICLE_CONTENT],
                   metadata={
                     ARTICLE_CATEGORY: item[ARTICLE_CATEGORY],
                     ARTICLE_URL: item[ARTICLE_URL],
                     ARTICLE_NAME: item[ARTICLE_NAME]
                   })
    documents.append(doc)
  return documents
