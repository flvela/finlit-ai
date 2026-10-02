"""tests the client response logger"""
from datetime import date
import os

from testutils.common import read_json_file
from tools.client_response_logger import ClientResponseFileLogger

TEST_PERSIST_DIRECTORY = "data/portfolio/mock_data/client_logger/"
TEST_TICKER = "IBM"
TEST_FUNCTION = "TIME_SERIES_DAILY"
TEST_RESPONSE_JSON_FILE = "data/portfolio/mock_data/ibm_global_quote.json"
TEST_PARAMS = {
  "maturity": "3month",
  "interval": "monthly"
}
TEST_TREASURY_YIELD_JSON_FILE = "data/portfolio/mock_data/treasury_yield_maturity_10year.json"


def test_client_response_file_logger_constructor():
  """tests the constructor for ClientResponseFileLogger"""
  client = ClientResponseFileLogger(persist_directory=TEST_PERSIST_DIRECTORY)
  assert client.persist_directory == TEST_PERSIST_DIRECTORY


def test_client_response_file_logger_get_persist_file_name():
  """tests the get_persist_file_name for ClientResponseFileLogger"""
  client = ClientResponseFileLogger(persist_directory=TEST_PERSIST_DIRECTORY)
  today = date.today()
  file_name = client.get_persist_file_name(function=TEST_FUNCTION, ticker=TEST_TICKER)
  assert TEST_FUNCTION.lower() in file_name
  assert TEST_TICKER.lower() in file_name
  assert str(today) in file_name


def test_client_response_file_logger_persist_and_get_response():
  """tests the persist_response and get_response functions of ClientResponseFileLogger"""
  try:
    client = ClientResponseFileLogger(persist_directory=TEST_PERSIST_DIRECTORY)
    response_json = read_json_file(TEST_RESPONSE_JSON_FILE)
    client.persist_response(function=TEST_FUNCTION, ticker=TEST_TICKER, response=response_json)
    persisted_response_json = client.get_response(function=TEST_FUNCTION, ticker=TEST_TICKER)
    assert response_json == persisted_response_json
  finally:
    # remove file once test is completed
    os.remove(client.get_persist_file_name(function=TEST_FUNCTION, ticker=TEST_TICKER))


def test_client_response_file_logger_get_persist_file_name_non_ticker():
  """tests the get_persist_file_name_non_ticker for ClientResponseFileLogger"""
  client = ClientResponseFileLogger(persist_directory=TEST_PERSIST_DIRECTORY)
  today = date.today()
  file_name = client.get_persist_file_name_non_ticker(function=TEST_FUNCTION, params=TEST_PARAMS)
  assert TEST_FUNCTION.lower() in file_name
  for key, value in TEST_PARAMS.items():
    assert key in file_name
    assert value in file_name
  assert str(today) in file_name


def test_client_response_file_logger_persist_and_get_response_non_ticker():
  """tests the persist_response_non_ticker and get_response get_response_non_ticker of ClientResponseFileLogger"""
  try:
    client = ClientResponseFileLogger(persist_directory=TEST_PERSIST_DIRECTORY)
    response_json = read_json_file(TEST_TREASURY_YIELD_JSON_FILE)
    client.persist_response_non_ticker(function=TEST_FUNCTION, params=TEST_PARAMS, response=response_json)
    persisted_response_json = client.get_response_non_ticker(function=TEST_FUNCTION, params=TEST_PARAMS)
    assert response_json == persisted_response_json
  finally:
    # remove file once test is completed
    os.remove(client.get_persist_file_name_non_ticker(function=TEST_FUNCTION, params=TEST_PARAMS))
