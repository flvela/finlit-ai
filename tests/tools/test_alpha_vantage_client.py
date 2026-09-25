"""Unit tests for AlphaVantage client API"""
from unittest.mock import patch

import requests
from tools.alpha_vantage_client import (
  BASE_URL,
  DEFAULT_TTL,
  DEMO_API_KEY,
  REQUEST_TIMEOUT,
  TIME_SERIES_DAILY_FUNCTION,
  AlphaVantageClient
)


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
  client = AlphaVantageClient()
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


@patch("requests.get")
def test_get_and_cache_request_timeout(mock_get):
  """tests the get_and_cache_request with timeout exception"""
  client = AlphaVantageClient()
  mock_get.side_effect = requests.exceptions.Timeout("Request timed out.")
  response = client.get_and_cache_request(TIME_SERIES_DAILY_FUNCTION, {})
  expected_url = f"{BASE_URL}{TIME_SERIES_DAILY_FUNCTION}&apikey={DEMO_API_KEY}"

  assert response is None
  mock_get.assert_called_once_with(expected_url, timeout=REQUEST_TIMEOUT)
