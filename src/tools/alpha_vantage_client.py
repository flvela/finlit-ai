"""Creates a client for AlphaVantage requests"""
from dataclasses import dataclass
from datetime import datetime

import requests
from cachetools import TTLCache
import pandas as pd

from tools.logger import get_logger

BASE_URL = "https://www.alphavantage.co/query?function="
DEFAULT_TTL = 216000  # 1 hour default cach TTL (60s*60*60)
DEMO_API_KEY = "demo"
TIME_SERIES_DAILY_FUNCTION = "TIME_SERIES_DAILY"
REQUEST_TIMEOUT = 2
CACHE_SIZE = 10

# CONSTANTS for parser
TIME_SERIES_DAILY_KEY = "Time Series (Daily)"
DATE_KEY = "date"
TICKER_KEY = "ticker"

# Columns for time series dataframe
OPEN_COLUMN = "1. open"
HIGH_COLUMN = "2. high"
LOW_COLUMN = "3. low"
CLOSE_COLUMN = "4. close"
VOLUMNE_COLUMN = "5. volumne"

logger = get_logger(__name__)


@dataclass
class AlphaVantageClient:
  """implements a HTTP client for alphavantage.co API"""
  ttl: int
  function_caches: dict[str, TTLCache]
  api_key: str
  call_count: int

  def __init__(self, ttl=DEFAULT_TTL, api_key=DEMO_API_KEY):
    self.ttl = ttl
    self.function_caches = {}
    self.api_key = api_key
    self.call_count = 0

  def time_series_daily(self, ticker: str):
    """get the time series daily value for the given ticker symbol"""
    params = {"symbol": ticker}

    if TIME_SERIES_DAILY_FUNCTION not in self.function_caches:
      self.function_caches[TIME_SERIES_DAILY_FUNCTION] = TTLCache(CACHE_SIZE, ttl=self.ttl)

    if ticker not in self.function_caches[TIME_SERIES_DAILY_FUNCTION]:
      response = self.get_and_cache_request(
        TIME_SERIES_DAILY_FUNCTION, params)
      self.function_caches[TIME_SERIES_DAILY_FUNCTION][ticker] = self.parse_time_series_daily(ticker, response)
    return self.function_caches[TIME_SERIES_DAILY_FUNCTION][ticker]

  def get_and_cache_request(self, function: str, params: dict[str, str]):
    """generic method to make HTTP requests to alphavantage API"""
    url_params = ""
    if len(params) > 0:
      url_params = "&".join(f"{key}={value}" for key, value in params.items())
      url = f"{BASE_URL}{function}&{url_params}&apikey={self.api_key}"
    else:
      url = f"{BASE_URL}{function}&apikey={self.api_key}"
    logger.info("making request to %s", url)
    self.call_count += 1
    try:
      response = requests.get(url, timeout=REQUEST_TIMEOUT).json()
      logger.info("request to %s responsed with %.400s...", url, response)
      return response
    except requests.exceptions.Timeout:
      logger.warning("The request to %s timed out after %d s", url, REQUEST_TIMEOUT)
      return None

  def parse_time_series_daily(self, ticker, response):
    """parses raw http request as time series dict"""
    if TIME_SERIES_DAILY_KEY not in response:
      logger.warning("could not parse time series response due to key %s not found %s", TIME_SERIES_DAILY_KEY, response)
      return None
    time_series = []
    for date, time_series_values in response[TIME_SERIES_DAILY_KEY].items():
      time_series_entry = {
        DATE_KEY: datetime.strptime(date, "%Y-%m-%d"),
        TICKER_KEY: ticker}
      for key, value in time_series_values.items():
        time_series_entry[key] = float(value)
      time_series.append(time_series_entry)

    time_series_df = pd.DataFrame(time_series)
    logger.info("parsed df %s", time_series_df.head(5))
    return time_series_df
