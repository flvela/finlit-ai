"""Common utils used for unit tests"""
import json

from langgraph.runtime import Runtime

from agents.context_schema import ContextSchema
from tools.alpha_vantage_client import (
  COMPANY_LOGO_FUNCTION,
  GLOBAL_QUOTE_FUNCTION,
  NEWS_SENTIMENT_FUNCTION,
  TREASURY_YIELD_FUNCTION
)
from tools.config import Config

URL_KEY = "URL"
MOCK_DATA_KEY = "MOCK_DATA"
TEST_URL_AND_MOCK_MAPPING = {
  COMPANY_LOGO_FUNCTION: {
    URL_KEY: "https://www.alphavantage.co/query?function=COMPANY_LOGO&symbol=IBM&apikey=demo",
    MOCK_DATA_KEY: "data/portfolio/mock_data/ibm_company_logo.json"
  },
  NEWS_SENTIMENT_FUNCTION: {
    URL_KEY: "https://www.alphavantage.co/query?function=NEWS_SENTIMENT&symbol=AAPL&apikey=demo",
    MOCK_DATA_KEY: "data/portfolio/mock_data/aapl_news_sentiment.json"
  },
  GLOBAL_QUOTE_FUNCTION: {
    URL_KEY: "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=demo",
    MOCK_DATA_KEY: "data/portfolio/mock_data/ibm_global_quote.json"
  },
  TREASURY_YIELD_FUNCTION: {
    URL_KEY: "https://www.alphavantage.co/query?function=TREASURY_YIELD&interval=monthly&maturity=10year&apikey=demo",
    MOCK_DATA_KEY: "data/portfolio/mock_data/treasury_yield_maturity_10year.json"
  }
}


def init_test_runtime():
  """test runtime initialization for LangGraph agents"""
  config = Config()
  context = ContextSchema(article_collection=None, llm=config.get_llm())
  return Runtime(context=context)


def read_json_file(json_file):
  """reads the given json file"""
  with open(json_file, "r", encoding="utf-8") as file:
    return json.load(file)
