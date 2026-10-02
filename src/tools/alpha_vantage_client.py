"""Creates a client for AlphaVantage requests"""
from dataclasses import dataclass
from datetime import datetime
import time
from typing import Callable, Literal

import requests
from cachetools import TTLCache
import pandas as pd

from tools.client_response_logger import ClientResponseFileLogger
from tools.logger import get_logger

BASE_URL = "https://www.alphavantage.co/query?function="
DEFAULT_TTL = 36000  # 1 hour default cach TTL (60s*60)
DAILY_TTL = 86400
DEMO_API_KEY = "demo"
TIME_SERIES_DAILY_FUNCTION = "TIME_SERIES_DAILY"
OVERVIEW_FUNCTION = "OVERVIEW"
COMPANY_LOGO_FUNCTION = "COMPANY_LOGO"
NEWS_SENTIMENT_FUNCTION = "NEWS_SENTIMENT"
GLOBAL_QUOTE_FUNCTION = "GLOBAL_QUOTE"
TREASURY_YIELD_FUNCTION = "TREASURY_YIELD"
REQUEST_TIMEOUT = 2
CACHE_SIZE = 10
MAX_RETRIES = 3

# CONSTANTS for parser
TIME_SERIES_DAILY_KEY = "Time Series (Daily)"
DATE_KEY = "date"
TICKER_KEY = "ticker"
LOGO_URL_PNG_KEY = "logo_url_png"
INFORMATION_KEY = "Information"
FREE_API_LIMIT_WARNING = "You may subscribe to any of the premium plans"
DEMO_KEY_WARNING = "Please query the demo URLs at no more than 2 requests per second."
GLOBAL_QUOTE_KEY = "Global Quote"

# Columns for time series dataframe
OPEN_COLUMN = "1. open"
HIGH_COLUMN = "2. high"
LOW_COLUMN = "3. low"
CLOSE_COLUMN = "4. close"
VOLUMNE_COLUMN = "5. volumne"

# PARAMETERS for TREASURY_YIELD function
MATURITY_PARAM = "maturity"
INTERVAL_PARAM = "interval"

# Persist directory to store response due to daily limits (ie. 25 request/day) for free tier
PERSIST_DIRECTORY = "data/portfolio/alpha_vantage/real_data/"

logger = get_logger(__name__)

TreasuryYieldMaturity = Literal["3month", "2year", "5year", "7year", "10year", "30year"]
TreasuryYieldInterval = Literal["daily", "weekly", "monthly"]


@dataclass
class AlphaVantageClient:
  """implements a HTTP client for alphavantage.co API"""
  ttl: int
  function_caches: dict[str, TTLCache]
  api_key: str
  call_count: int
  client_response_logger: ClientResponseFileLogger

  def __init__(self, ttl=DEFAULT_TTL, api_key=DEMO_API_KEY, persist_directory=PERSIST_DIRECTORY):
    self.ttl = ttl
    self.function_caches = {}
    self.api_key = api_key
    self.call_count = 0
    self.client_response_logger = ClientResponseFileLogger(persist_directory=persist_directory)

  def time_series_daily(self, ticker: str):
    """get the time series daily value for the given ticker symbol"""
    params = {"symbol": ticker}
    return self.get_and_cache_request_by_ticker(
      function=TIME_SERIES_DAILY_FUNCTION,
      params=params,
      ticker=ticker,
      parse_method=self.parse_time_series_daily)

  def overview(self, ticker: str):
    """get the overview for a given ticker"""
    params = {"symbol": ticker}
    return self.get_and_cache_request_by_ticker(
      function=OVERVIEW_FUNCTION,
      params=params,
      ticker=ticker,
      parse_method=self.no_op_parser
    )

  def company_logo(self, ticker: str):
    """get the company logo"""
    params = {"symbol": ticker}
    return self.get_and_cache_request_by_ticker(
      function=COMPANY_LOGO_FUNCTION,
      params=params,
      ticker=ticker,
      parse_method=self.company_logo_parser
    )

  def news_sentiment(self, ticker: str):
    """get the news sentiment"""
    params = {"symbol": ticker}
    return self.get_and_cache_request_by_ticker(
      function=NEWS_SENTIMENT_FUNCTION,
      params=params,
      ticker=ticker,
      parse_method=self.no_op_parser
    )

  def global_quote(self, ticker: str):
    """get the global quote for ticker"""
    params = {"symbol": ticker}
    return self.get_and_cache_request_by_ticker(
      function=GLOBAL_QUOTE_FUNCTION,
      params=params,
      ticker=ticker,
      parse_method=self.global_quote_parser
    )

  def get_treasury_yield(self, maturity: TreasuryYieldMaturity = "10year", interval: TreasuryYieldInterval = "monthly"):
    """gets the Treasury yield for the given maturity"""
    if TREASURY_YIELD_FUNCTION not in self.function_caches:
      self.function_caches[TREASURY_YIELD_FUNCTION] = TTLCache(CACHE_SIZE, ttl=self.ttl)

    if maturity not in self.function_caches[TREASURY_YIELD_FUNCTION]:
      params = {MATURITY_PARAM: maturity, INTERVAL_PARAM: interval}
      response = self.client_response_logger.get_response_non_ticker(TREASURY_YIELD_FUNCTION, params=params)
      cache_key = f"{maturity}_{interval}"
      if response is None:
        response = self.get_request(TREASURY_YIELD_FUNCTION, params=params)
        self.client_response_logger.persist_response_non_ticker(TREASURY_YIELD_FUNCTION, params=params, response=response)
      self.function_caches[TREASURY_YIELD_FUNCTION][cache_key] = response
    return self.function_caches[TREASURY_YIELD_FUNCTION][cache_key]

  def get_and_cache_request_by_ticker(self, function: str, params: dict[str, str], ticker: str, parse_method: Callable):
    """generic function that makes request to alpha vantage API and caches response after parsing it
       Parsing method must take ticker and request.get response as parameters and return a type to be cached
    """
    if function not in self.function_caches:
      self.function_caches[function] = TTLCache(CACHE_SIZE, ttl=self.ttl)

    if ticker not in self.function_caches[function]:
      # check client response logger to see if previous response was already made today
      response = self.client_response_logger.get_response(function=function, ticker=ticker)
      if response is None:
        response = self.get_request(function, params)
        self.client_response_logger.persist_response(function=function, ticker=ticker, response=response)
      self.function_caches[function][ticker] = parse_method(ticker, response)
    return self.function_caches[function][ticker]

  def get_request(self, function: str, params: dict[str, str], retries: int = 3):
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
      response = requests.get(url, timeout=REQUEST_TIMEOUT)
      response_json = response.json()
      logger.info("request to %s responsed with code %s and %s", url,
                  response.status_code, response_json)

      if (INFORMATION_KEY in response_json
          and (
            FREE_API_LIMIT_WARNING in response_json[INFORMATION_KEY]
            or DEMO_KEY_WARNING in response_json[INFORMATION_KEY]
          )
          and retries > 0):
        logger.warning("reached API limit for %url with response %s", url, response_json)
        time.sleep(1)
        return self.get_request(function, params, retries - 1)
      return response_json
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

  def company_logo_parser(self, ticker, response):
    """parses the company logo PNG url from the company_logo response"""
    return self.extract_key_from_response(ticker, response, LOGO_URL_PNG_KEY, COMPANY_LOGO_FUNCTION)

  def global_quote_parser(self, ticker, response):
    """parses the global quote data from the global_quote response"""
    return self.extract_key_from_response(ticker, response, GLOBAL_QUOTE_KEY, GLOBAL_QUOTE_FUNCTION)

  def extract_key_from_response(self, ticker, response, key, api_function):
    """extract a key from the response for given ticker and api function"""
    if response is None or key not in response:
      logger.warning("could not extract key %s from response %s for function %s and ticker %s",
                     key, response, api_function, ticker)
      return None
    return response[key]

  def no_op_parser(self, ticker, response):
    """when there is no operation to parse and we want raw response"""
    logger.info("called no_op_parser for ticker: %s and response: %s", ticker, response)
    return response
