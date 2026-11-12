"""Market and Portfolio analysis tools"""
import json

import pandas as pd

from langchain.tools import ToolRuntime, tool
from tools.alpha_vantage_client import TreasuryYieldInterval, TreasuryYieldMaturity
from tools.logger import get_logger
from tools.portfolio_manager import TREASURY_DATA_KEY, TREASURY_DATE_COLUMN

logger = get_logger(__name__)

@tool("get_time_series_daily",
      description="returns the daily OHLCV history (Open, High, Low, Close, Value) for a given ticker")
def get_time_series_daily(ticker: str, runtime: ToolRuntime):
  """
  Get the time series daily for a given ticker.
  the time series includes daily OHLCV history (Open, High, Low, Close, Value)

  Args:
    ticker (str): the ticker to search for
    runtime (ToolRuntime): the runtime environment for the tool
  """
  logger.info("getting time_series_daily for %s", ticker)
  return json.dumps(runtime.context.portfolio_manager.get_time_series_daily(ticker).to_json())


@tool("get_global_quote",
      description="get the current open, high, low, price, volumne,"
      "latest trading day, previous close, change and change percent for a given ticker")
def get_global_quote(ticker: str, runtime: ToolRuntime):
  """
  Get the current global quote for a given ticker.
  global quote includes current open, high, low, price, volumne
  latest trading day, previous close, change and change percent for a given ticker

  Args:
    ticker (str): the ticker to search for
    runtime (ToolRuntime): the runtime environment for the tool
  """
  logger.info("getting global_quote for %s", ticker)
  return json.dumps(runtime.context.portfolio_manager.get_global_quote(ticker))


@tool("get_treasury_yield",
      description="gets the US Treasury(T-BILL) yield daily, weekly and monthly "
      "for a given maturity timeline (ie. 3month, 10year, etc)")
def get_treasury_yield(maturity: TreasuryYieldMaturity, interval: TreasuryYieldInterval, runtime: ToolRuntime):
  """
  Get the US treasury yield for daily, weekly and monthly for a given maturity timeline (ie. 3month, 10year, etc)

  Args:
    maturity (TreasuryYieldMaturity): maturity for the T-BILL (3month, 2year, 5year, 7year, 10year or 30year)
    interval (TreasuryYieldInterval): interval (daily, weekly, monthly)
    runtime (ToolRuntime): the runtime environment for the tool
  """
  logger.info("getting treasury yield for %s with interval %s", maturity, interval)
  # limit result to last 100 values.
  treasury_yield_response = runtime.context.portfolio_manager.get_treasury_yield(maturity, interval)
  treasury_yield_df = pd.DataFrame(treasury_yield_response[TREASURY_DATA_KEY])
  treasury_yield_df = treasury_yield_df.sort_values(by=TREASURY_DATE_COLUMN).tail(100)
  return json.dumps(treasury_yield_df.to_json())


@tool("get_ticker_overview",
      description="gets the ticker information including: asset type, industry, sector, exchange, currency, description,"
      "trailingPE, trailingPegRatio, MarketCap,ebitda, Analysist targets and ratings, Beta, etc..")
def get_ticker_overview(ticker: str, runtime: ToolRuntime):
  """
  gets the ticker information including: quote type, industry, sector, exchange, currency, description
  PE Ratio, PEG RATIO, MarketCap, Analysist targets and ratings, Beta, etc..

  Args:
    ticker (str): the ticker to search for
    runtime (ToolRuntime): the runtime environment for the tool
  """
  logger.info("getting ticker overview for %s", ticker)
  return json.dumps(runtime.context.market_manager.get_ticker_info(ticker))


@tool("get_portfolio_summary",
      description="gets the users portfolio that includes ticker,purchase_date,purchase_price,shares")
def get_portfolio_summary(runtime: ToolRuntime):
  """
  gets the users portfolio that includes ticker,purchase_date,purchase_price,shares

  Args:
    runtime (ToolRuntime): the runtime environment for the tool
  """
  return json.dumps(runtime.context.portfolio_manager.get_portfolio().to_json())
