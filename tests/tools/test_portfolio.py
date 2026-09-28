"""unit tests for portfolio store"""
from datetime import datetime
import json
import os

import pytest
from tools.alpha_vantage_client import AlphaVantageClient
from tools.portfolio import (
  COST_BASIS_COLUMN,
  DATE_FORMAT,
  PURCHASE_DATE_COLUMN,
  PURCHASE_PRICE_COLUMN,
  RUNNING_SHARES_TOTAL_COLUMN,
  SHARES_COLUMN,
  TICKER_COLUMN,
  CSVPortfolioStore,
  PortfolioManager
)

TEST_INPUT_CSV = """ticker,purchase_date,purchase_price,shares
IBM,2021-12-31,133.66,12.0
MSFT,2026-03-31,333.15,11.8
MSFT,2026-03-31,333.15,11.8
IBM,2026-08-21,235.68,25.0
"""
TEST_INPUT_CSV_FILE_NAME = "data/input.csv"
TEST_NEW_FILE_NAME = "data/new.csv"

TEST_IBM_TIME_SERIES_URL = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=demo"
TEST_MSFT_TIME_SERIES_URL = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey=demo"
TEST_IBM_TIME_SERIES_JSON_PATH = "data/portfolio/mock_data/ibm_time_series_daily.json"
TEST_MSFT_TIME_SERIES_JSON_PATH = "data/portfolio/mock_data/msft_time_series_daily.json"

test_data = [
  (False, 0),
  (True, 4)
]
TEST_ALPHA_VANTAGE_KEY = "demo"


def write_to_file(file_name, value):
  """writes to a file based on file name and value"""
  with open(file_name, "w", encoding="utf-8") as file:
    file.write(value)


@pytest.mark.parametrize("file_exists, expected_size", test_data)
def test_csv_portfolio_store_init(file_exists: str, expected_size: int):
  """tests the CSVPortfolio constructor"""
  try:
    if file_exists:
      write_to_file(TEST_INPUT_CSV_FILE_NAME, TEST_INPUT_CSV)
    portfolio = CSVPortfolioStore(TEST_INPUT_CSV_FILE_NAME)
    assert len(portfolio.df) == expected_size
    assert portfolio.portfolio_csv == TEST_INPUT_CSV_FILE_NAME
  finally:
    if file_exists:
      os.remove(TEST_INPUT_CSV_FILE_NAME)


def test_csv_portfolio_add_purchase():
  """tests the add_purchase functionality for CSVPortfolioStore"""

  try:
    # originally new.csv does not exist
    assert os.path.exists(TEST_NEW_FILE_NAME) is False
    portfolio = CSVPortfolioStore(TEST_NEW_FILE_NAME)
    assert len(portfolio.df) == 0
    ticker = "APPL"
    purchase_date = "2025-09-25"
    purchase_price = 300.23
    shares = 20
    portfolio.add_purchase(ticker, purchase_date, purchase_price, shares)
    assert len(portfolio.df) == 1
    row_dict = portfolio.df.loc[0].to_dict()
    assert row_dict[TICKER_COLUMN] == ticker
    assert row_dict[PURCHASE_PRICE_COLUMN] == purchase_price
    assert row_dict[PURCHASE_DATE_COLUMN].strftime(DATE_FORMAT) == purchase_date
    assert row_dict[SHARES_COLUMN] == shares
    assert row_dict[COST_BASIS_COLUMN] == purchase_price * shares
    # after adding purchase a new file is created
    assert os.path.exists(TEST_NEW_FILE_NAME) is True
  finally:
    # clean up file
    os.remove(TEST_NEW_FILE_NAME)


def test_csv_portfolio_import_csv():
  """tests the import_csv for CSVPortfolioStore"""
  new_file = TEST_NEW_FILE_NAME

  try:
    # originally new.csv does not exist
    assert os.path.exists(new_file) is False
    portfolio = CSVPortfolioStore(new_file)
    assert len(portfolio.df) == 0
    write_to_file(TEST_INPUT_CSV_FILE_NAME, TEST_INPUT_CSV)
    portfolio.import_csv(TEST_INPUT_CSV_FILE_NAME)
    assert len(portfolio.df) == 4
    previous_date = None
    for _, row in portfolio.df.iterrows():
      if previous_date is not None:
        assert row[PURCHASE_DATE_COLUMN] >= previous_date
      assert row[COST_BASIS_COLUMN] == row[PURCHASE_PRICE_COLUMN] * row[SHARES_COLUMN]
      previous_date = row[PURCHASE_DATE_COLUMN]
  finally:
    # clean up file
    os.remove(new_file)
    os.remove(TEST_INPUT_CSV_FILE_NAME)


def test_csv_portfolio_get_portfolio():
  """test the get_portfolio for CSVPortfolioStore"""
  new_file = TEST_NEW_FILE_NAME

  try:
    # originally new.csv does not exist
    assert os.path.exists(new_file) is False
    portfolio = CSVPortfolioStore(new_file)
    assert len(portfolio.df) == 0
    ticker = "APPL"
    purchase_date = "2025-09-25"
    purchase_price = 300.23
    shares = 20
    portfolio.add_purchase(ticker, purchase_date, purchase_price, shares)
    assert len(portfolio.get_portfolio()) == 1
  finally:
    # clean up file
    os.remove(new_file)


def test_portfolio_manager_init():
  """tests the portfolio manager init"""
  portfolio_manager = PortfolioManager(alpha_vantage_key=TEST_ALPHA_VANTAGE_KEY, portfolio_csv=TEST_NEW_FILE_NAME)
  assert isinstance(portfolio_manager.alpha_vantage_client, AlphaVantageClient)
  assert isinstance(portfolio_manager.portfolio_store, CSVPortfolioStore)
  assert isinstance(portfolio_manager.last_update_time_series, datetime)
  assert portfolio_manager.alpha_vantage_client.api_key == TEST_ALPHA_VANTAGE_KEY
  assert portfolio_manager.portfolio_store.portfolio_csv == TEST_NEW_FILE_NAME


def test_portfolio_manager_add_purchase():
  """tests the portfolio manager add_purchase method"""
  try:
    portfolio_manager = PortfolioManager(alpha_vantage_key=TEST_ALPHA_VANTAGE_KEY, portfolio_csv=TEST_NEW_FILE_NAME)
    assert len(portfolio_manager.get_portfolio()) == 0
    ticker = "APPL"
    purchase_date = "2025-09-25"
    purchase_price = 300.23
    shares = 20
    portfolio_manager.add_purchase(ticker, purchase_date, purchase_price, shares)
    assert len(portfolio_manager.get_portfolio()) == 1
  finally:
    # clean up portfolio store
    os.remove(TEST_NEW_FILE_NAME)


def test_portfolio_manager_import_csv():
  """tests the portfolio manager import_csv method"""
  try:
    portfolio_manager = PortfolioManager(alpha_vantage_key=TEST_ALPHA_VANTAGE_KEY, portfolio_csv=TEST_NEW_FILE_NAME)
    assert len(portfolio_manager.get_portfolio()) == 0
    write_to_file(TEST_INPUT_CSV_FILE_NAME, TEST_INPUT_CSV)
    portfolio_manager.import_csv(TEST_INPUT_CSV_FILE_NAME)
    assert len(portfolio_manager.get_portfolio()) == 4
  finally:
    os.remove(TEST_NEW_FILE_NAME)
    os.remove(TEST_INPUT_CSV_FILE_NAME)


test_time_series_data = [
  (False, 0),  # no tickers means no time series
  (True, 200),  # 100 entries per ticker and 2 tickers (MSFT, IBM) means 200 entries
]


@pytest.mark.parametrize("has_portfolio_data, expected_time_series_size", test_time_series_data)
def test_portfolio_manager_time_series_daily(has_portfolio_data, expected_time_series_size):
  """tests the portfolio manager get_time_series_daily method"""
  try:
    if has_portfolio_data:
      write_to_file(TEST_NEW_FILE_NAME, TEST_INPUT_CSV)
    portfolio_manager = PortfolioManager(alpha_vantage_key=TEST_ALPHA_VANTAGE_KEY, portfolio_csv=TEST_NEW_FILE_NAME)
    time_series_df = portfolio_manager.get_time_series_daily()
    assert len(time_series_df) == expected_time_series_size
  finally:
    if has_portfolio_data:
      os.remove(TEST_NEW_FILE_NAME)


def test_portfolio_manager_get_portfolio_with_running_total_shares():
  """tests the portfolio manager get_portfolio_with_running_total_shares method"""
  try:
    write_to_file(TEST_NEW_FILE_NAME, TEST_INPUT_CSV)
    portfolio_manager = PortfolioManager(alpha_vantage_key=TEST_ALPHA_VANTAGE_KEY, portfolio_csv=TEST_NEW_FILE_NAME)
    portfolio_df = portfolio_manager.get_portfolio_with_running_total_shares()
    assert len(portfolio_df) == 4
    previous_date = None
    previous_ticker = None
    running_share_total = 0
    for _, row in portfolio_df.iterrows():
      if previous_ticker is not None and previous_ticker != row[TICKER_COLUMN]:
        # date and running share total resets
        previous_date = None
        running_share_total = 0
      if previous_date is not None:
        assert row[PURCHASE_DATE_COLUMN] >= previous_date
      running_share_total += row[SHARES_COLUMN]
      assert row[RUNNING_SHARES_TOTAL_COLUMN] == running_share_total
      previous_ticker = row[TICKER_COLUMN]
  finally:
    os.remove(TEST_NEW_FILE_NAME)


def read_json_file(json_file):
  """reads the given json file"""
  with open(json_file, "r", encoding="utf-8") as file:
    return json.load(file)


def test_portfolio_manager_get_portfolio_summary_df(requests_mock):
  """tests the PortfolioManager get_portfolio_summary_df"""
  try:
    write_to_file(TEST_NEW_FILE_NAME, TEST_INPUT_CSV)
    requests_mock.get(TEST_IBM_TIME_SERIES_URL,
                      json=read_json_file(TEST_IBM_TIME_SERIES_JSON_PATH),
                      status_code=200)
    requests_mock.get(TEST_MSFT_TIME_SERIES_URL,
                      json=read_json_file(TEST_MSFT_TIME_SERIES_JSON_PATH),
                      status_code=200)
    portfolio_manager = PortfolioManager(alpha_vantage_key=TEST_ALPHA_VANTAGE_KEY, portfolio_csv=TEST_NEW_FILE_NAME)
    portfolio_summary_df = portfolio_manager.get_portfolio_summary_df()
    # 100 entries per ticker and 2 tickers (MSFT, IBM) = 200
    assert len(portfolio_summary_df) == 200
  finally:
    os.remove(TEST_NEW_FILE_NAME)


def test_portfolio_manager_get_portfolio_positions_df(requests_mock):
  """tests the PortfolioManager get_portfolio_positions_df"""
  try:
    write_to_file(TEST_NEW_FILE_NAME, TEST_INPUT_CSV)
    requests_mock.get(TEST_IBM_TIME_SERIES_URL,
                      json=read_json_file(TEST_IBM_TIME_SERIES_JSON_PATH),
                      status_code=200)
    requests_mock.get(TEST_MSFT_TIME_SERIES_URL,
                      json=read_json_file(TEST_MSFT_TIME_SERIES_JSON_PATH),
                      status_code=200)
    portfolio_manager = PortfolioManager(alpha_vantage_key=TEST_ALPHA_VANTAGE_KEY, portfolio_csv=TEST_NEW_FILE_NAME)
    portfolio_positions_df = portfolio_manager.get_portfolio_positions_df()
    assert len(portfolio_positions_df) == 4
  finally:
    os.remove(TEST_NEW_FILE_NAME)
