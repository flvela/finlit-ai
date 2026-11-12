"""unit tests for market_manager"""
import collections
import json

from testutils.common import write_to_file
from tools.market_manager import Y_FINANCE_INDICES_DF_FIELDS, Y_FINANCE_TICKER_INFO_FIELDS, MarketManager


TEST_NEW_FILE = "data/test.json"
TEST_TICKER = "IBM"

def test_market_manager_get_us_market_indices_df():
  """tests the MarketManager get_us_market_indices_df"""
  market_manager = MarketManager()
  indices_summary_df = market_manager.get_us_market_indices_df()
  # 251 entries per ticker and 3 tickers () = 753
  assert len(indices_summary_df) == 753
  assert collections.Counter(indices_summary_df.columns.to_list()) == collections.Counter(Y_FINANCE_INDICES_DF_FIELDS)

def test_market_manager_ticker_info():
  """tests the MarketManager get_ticker_info"""

  market_manager = MarketManager()
  ticker_info = market_manager.get_ticker_info(TEST_TICKER)
  for field in Y_FINANCE_TICKER_INFO_FIELDS:
    assert field in ticker_info
  write_to_file(TEST_NEW_FILE, json.dumps(ticker_info))
