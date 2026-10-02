"""class to log client response to file"""
from dataclasses import dataclass
from datetime import date
import json
import os

from tools.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ClientResponseFileLogger:
  """Client Response file logger logs a json response to file in a given persist directory"""
  persist_directory: str

  def __init__(self, persist_directory: str):
    self.persist_directory = persist_directory
    # Ensure the directory exists before we can write to it
    directory = os.path.dirname(persist_directory)
    logger.info("directory %s, persist_directory %s, os.path.exists %s", directory,
                persist_directory, os.path.exists(directory))
    if directory and not os.path.exists(directory):
      os.makedirs(directory)

  def get_persist_file_name(self, function: str, ticker: str):
    """get the persistance file name based on function and ticker"""
    return f"{self.persist_directory}/{ticker.lower()}_{function.lower()}_{date.today()}.json"

  def persist_response(self, function: str, ticker: str, response):
    """persist the response received by calling function and ticker"""
    file_name = self.get_persist_file_name(function=function, ticker=ticker)

    with open(file_name, "w+", encoding="utf-8") as file:
      json.dump(response, file)
    logger.info("persisted response %200s... to file %s for ticker %s and function %s", response, file_name, ticker, function)

  def get_response(self, function: str, ticker: str):
    """gets the response from the persistance file based on ticker and function"""
    file_name = self.get_persist_file_name(function=function, ticker=ticker)
    if os.path.exists(file_name):
      with open(file_name, "r", encoding="utf-8") as file:
        response = json.load(file)
        logger.info("read response %200s... from file %s for ticker %s and function %s", response, file_name, ticker, function)
        return response
    else:
      return None

  def get_persist_file_name_non_ticker(self, function: str, params: dict[str, str]):
    """get the persistance file name based on function and params"""
    params_str = "_".join(f"{key}_{value}" for key, value in params.items())
    return f"{self.persist_directory}/{function.lower()}_{params_str.lower()}_{date.today()}.json"

  def persist_response_non_ticker(self, function: str, params: dict[str, str], response):
    """persist the response received by calling a non-ticker function with params"""
    file_name = self.get_persist_file_name_non_ticker(function=function, params=params)

    with open(file_name, "w+", encoding="utf-8") as file:
      json.dump(response, file)
    logger.info("persisted response %200s... to file %s for params %s and function %s", response, file_name, params, function)

  def get_response_non_ticker(self, function: str, params: dict[str, str]):
    """gets the response from the persistance file based on params and function"""
    file_name = self.get_persist_file_name_non_ticker(function=function, params=params)
    if os.path.exists(file_name):
      with open(file_name, "r", encoding="utf-8") as file:
        response = json.load(file)
        logger.info("read response %200s... from file %s for params %s and function %s", response, file_name, params, function)
        return response
    else:
      return None
