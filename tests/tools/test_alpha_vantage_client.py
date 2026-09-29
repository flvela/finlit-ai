"""Unit tests for AlphaVantage client API"""
import os
from unittest.mock import patch

import requests
from testutils.common import MOCK_DATA_KEY, TEST_URL_AND_MOCK_MAPPING, URL_KEY, read_json_file
from tools.alpha_vantage_client import (
  BASE_URL,
  COMPANY_LOGO_FUNCTION,
  DEFAULT_TTL,
  DEMO_API_KEY,
  GLOBAL_QUOTE_FUNCTION,
  INTERVAL_PARAM,
  MATURITY_PARAM,
  NEWS_SENTIMENT_FUNCTION,
  OVERVIEW_FUNCTION,
  REQUEST_TIMEOUT,
  TIME_SERIES_DAILY_FUNCTION,
  TREASURY_YIELD_FUNCTION,
  AlphaVantageClient
)
TEST_PERSIST_DIRECTORY = "data/portfolio/mock_data/client_logger/"


def test_alpha_vantage_client_init():
  """unit test for AlphaVantageClient constructor"""
  # test default params
  client = AlphaVantageClient()
  assert client.ttl == DEFAULT_TTL
  assert client.api_key == DEMO_API_KEY
  assert len(client.function_caches) == 0
  assert client.call_count == 0

  ttl = 60
  api_key = "new_key"
  client = AlphaVantageClient(ttl, api_key)
  assert client.ttl == 60
  assert client.api_key == api_key
  assert len(client.function_caches) == 0
  assert client.call_count == 0


def test_alpha_vantage_time_series_daily():
  """unit test for AlphaVantageClient time_series_daily"""
  try:
    client = AlphaVantageClient(persist_directory=TEST_PERSIST_DIRECTORY)
    ticker = "IBM"  # use IBM as it works with the demo key
    response = client.time_series_daily(ticker)
    assert response is not None
    assert client.call_count == 1
    assert len(client.function_caches) == 1
    assert TIME_SERIES_DAILY_FUNCTION in client.function_caches
    assert ticker in client.function_caches[TIME_SERIES_DAILY_FUNCTION]
    cached_response = client.function_caches[TIME_SERIES_DAILY_FUNCTION][ticker]
    assert response.equals(cached_response)

    # make the call again expecting call count to not increase but to have the same cached_response
    response = client.time_series_daily(ticker)
    assert response is not None
    assert client.call_count == 1
    assert response.equals(cached_response)
  finally:
    os.remove(client.client_response_logger.get_persist_file_name(ticker=ticker, function=TIME_SERIES_DAILY_FUNCTION))


@patch("requests.get")
def test_get_and_cache_request_timeout(mock_get):
  """tests the get_and_cache_request with timeout exception"""
  client = AlphaVantageClient(persist_directory=TEST_PERSIST_DIRECTORY)
  mock_get.side_effect = requests.exceptions.Timeout("Request timed out.")
  response = client.get_request(TIME_SERIES_DAILY_FUNCTION, {})
  expected_url = f"{BASE_URL}{TIME_SERIES_DAILY_FUNCTION}&apikey={DEMO_API_KEY}"

  assert response is None
  mock_get.assert_called_once_with(expected_url, timeout=REQUEST_TIMEOUT)


def test_alpha_vantage_overview():
  """unit test for AlphaVantageClient overview"""
  try:
    client = AlphaVantageClient(persist_directory=TEST_PERSIST_DIRECTORY)
    ticker = "IBM"  # use IBM as it works with the demo key
    response = client.overview(ticker)
    assert response is not None
    assert client.call_count == 1
    assert len(client.function_caches) == 1
    assert OVERVIEW_FUNCTION in client.function_caches
    assert ticker in client.function_caches[OVERVIEW_FUNCTION]
    cached_response = client.function_caches[OVERVIEW_FUNCTION][ticker]
    assert response == cached_response

    # make the call again expecting call count to not increase but to have the same cached_response
    response = client.overview(ticker)
    assert response is not None
    assert client.call_count == 1
    assert response == cached_response
  finally:
    os.remove(client.client_response_logger.get_persist_file_name(ticker=ticker, function=OVERVIEW_FUNCTION))


def api_request_mock_helper(client: AlphaVantageClient, client_function: callable,
                            ticker: str, api_function: str, requests_mock):
  """helper method that mocks downstream requests and asserts failures"""
  url = TEST_URL_AND_MOCK_MAPPING[api_function][URL_KEY]
  mock_data = TEST_URL_AND_MOCK_MAPPING[api_function][MOCK_DATA_KEY]
  requests_mock.get(url, json=read_json_file(mock_data), status_code=200)

  response = client_function(ticker)
  assert response is not None
  assert client.call_count == 1
  assert len(client.function_caches) == 1
  assert api_function in client.function_caches
  assert ticker in client.function_caches[api_function]
  cached_response = client.function_caches[api_function][ticker]
  assert response == cached_response

  # make the call again expecting call count to not increase but to have the same cached_response
  response = client_function(ticker)
  assert response is not None
  assert client.call_count == 1
  assert response == cached_response


def test_alpha_vantage_news_sentiment(requests_mock):
  """unit test for AlphaVantageClient news_sentiment"""
  try:
    client = AlphaVantageClient(persist_directory=TEST_PERSIST_DIRECTORY)
    ticker = "AAPL"  # use AAPL as it works with the demo key
    api_request_mock_helper(client, client.news_sentiment, ticker, NEWS_SENTIMENT_FUNCTION, requests_mock)
  finally:
    os.remove(client.client_response_logger.get_persist_file_name(ticker=ticker, function=NEWS_SENTIMENT_FUNCTION))


def test_alpha_vantage_global_quote(requests_mock):
  """unit test for AlphaVantageClient global_quote"""
  try:
    client = AlphaVantageClient(persist_directory=TEST_PERSIST_DIRECTORY)
    ticker = "IBM"  # use IBM as it works with the demo key
    api_request_mock_helper(client, client.global_quote, ticker, GLOBAL_QUOTE_FUNCTION, requests_mock)
  finally:
    os.remove(client.client_response_logger.get_persist_file_name(ticker=ticker, function=GLOBAL_QUOTE_FUNCTION))


def test_alpha_vantage_company_logo(requests_mock):
  """unit test for AlphaVantageClient company_logo"""
  try:
    client = AlphaVantageClient(persist_directory=TEST_PERSIST_DIRECTORY)
    ticker = "IBM"  # use IBM as it works with the demo key
    api_request_mock_helper(client, client.company_logo, ticker, COMPANY_LOGO_FUNCTION, requests_mock)
  finally:
    os.remove(client.client_response_logger.get_persist_file_name(ticker=ticker, function=COMPANY_LOGO_FUNCTION))


def test_alpha_vantage_get_treasury_yield(requests_mock):
  """unit test for AlphaVantageClient get_treasury_yield"""
  try:
    client = AlphaVantageClient(persist_directory=TEST_PERSIST_DIRECTORY)
    url = TEST_URL_AND_MOCK_MAPPING[TREASURY_YIELD_FUNCTION][URL_KEY]
    mock_data = TEST_URL_AND_MOCK_MAPPING[TREASURY_YIELD_FUNCTION][MOCK_DATA_KEY]
    requests_mock.get(url, json=read_json_file(mock_data), status_code=200)

    maturity = "10year"
    interval = "monthly"
    cache_key = f"{maturity}_{interval}"

    response = client.get_treasury_yield(maturity=maturity, interval="monthly")
    assert response is not None
    assert client.call_count == 1
    assert len(client.function_caches) == 1
    assert TREASURY_YIELD_FUNCTION in client.function_caches
    assert cache_key in client.function_caches[TREASURY_YIELD_FUNCTION]
    cached_response = client.function_caches[TREASURY_YIELD_FUNCTION][cache_key]
    assert response == cached_response

    # make the call again expecting call count to not increase but to have the same cached_response
    response = client.get_treasury_yield(maturity=maturity)
    assert response is not None
    assert client.call_count == 1
    assert response == cached_response

  finally:
    os.remove(client.client_response_logger.get_persist_file_name_non_ticker
              (params={MATURITY_PARAM: maturity, INTERVAL_PARAM: interval}, function=TREASURY_YIELD_FUNCTION))
