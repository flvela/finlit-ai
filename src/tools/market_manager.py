"""defines the market manager class responsible for fetching/displaying market data"""
from dataclasses import dataclass

import pandas as pd
import yfinance as yf

from tools.logger import get_logger

Y_FINANCE_TICKER_COLUMN = "Ticker"
Y_FINANCE_DATE_COLUMN = "Date"
Y_FINANCE_OPEN_COLUMN = "Open"
Y_FINANCE_HIGH_COLUMN = "High"
Y_FINANCE_LOW_COLUMN = "Low"
Y_FINANCE_CLOSE_COLUMN = "Close"
Y_FINANCE_VOLUMNE_COLUMN = "Volume"
Y_FINANCE_DIVIDENDS_COLUMN = "Dividends"
Y_FINANCE_STOCK_SPLITS_COLUMN = "Stock Splits"
Y_FINANCE_PERCENT_CHANGE_COLUMN = "Percent_Change"
Y_FINANCE_TICKER_NAME_COLUMN = "Name"
Y_FINANCE_INDICES_DF_FIELDS = [Y_FINANCE_TICKER_COLUMN, Y_FINANCE_DATE_COLUMN, Y_FINANCE_OPEN_COLUMN,
                               Y_FINANCE_HIGH_COLUMN, Y_FINANCE_LOW_COLUMN, Y_FINANCE_CLOSE_COLUMN,
                               Y_FINANCE_VOLUMNE_COLUMN, Y_FINANCE_DIVIDENDS_COLUMN, Y_FINANCE_STOCK_SPLITS_COLUMN,
                               Y_FINANCE_PERCENT_CHANGE_COLUMN]

Y_FINANCE_TICKER_INFO_REGULAR_MARKET_CHANGE = "regularMarketChange"
Y_FINANCE_TICKER_INFO_REGULAR_MARKET_CHANGE_PERCENT = "regularMarketChangePercent"
Y_FINANCE_TICKER_INFO_REGULAR_MARKET_PRICE = "regularMarketPrice"
Y_FINANCE_TICKER_INFO_REGULAR_MARKET_TIME = "regularMarketTime"
Y_FINANCE_TICKER_INFO_SHORT_NAME = "shortName"
Y_FINANCE_TICKER_INFO_DISPLAY_NAME = "displayName"
Y_FINANCE_TICKER_INFO_FIELDS = [
  Y_FINANCE_TICKER_INFO_REGULAR_MARKET_CHANGE,
  Y_FINANCE_TICKER_INFO_REGULAR_MARKET_CHANGE_PERCENT,
  Y_FINANCE_TICKER_INFO_REGULAR_MARKET_PRICE,
  Y_FINANCE_TICKER_INFO_REGULAR_MARKET_TIME,
  Y_FINANCE_TICKER_INFO_SHORT_NAME
]

Y_FINANCE_SECTORS = [
  "basic-materials",
  "communication-services",
  "consumer-cyclical",
  "consumer-defensive",
  "energy",
  "financial-services",
  "healthcare",
  "industrials",
  "real-estate",
  "technology",
  "utilities"
]

logger = get_logger(__name__)


@dataclass
class MarketManager:
  """market manager class for displaying market indices, futures, market movers and top news"""

  def get_us_market_indices_df(self):
    """get the us market indices S&P500, NASDAQ, Dow Jones"""
    # ^GSPC - S&P 500, ^DJI - Dow Jones, ^IXIC Nasdaq Composite
    time_series_df = pd.DataFrame()
    for ticker in ["^GSPC", "^DJI", "^IXIC"]:
      idx = yf.Ticker(ticker=ticker)
      temp_df = idx.history(period="1y", interval="1d")
      temp_df[Y_FINANCE_TICKER_COLUMN] = ticker
      temp_df[Y_FINANCE_TICKER_NAME_COLUMN] = idx.info[Y_FINANCE_TICKER_INFO_SHORT_NAME]
      temp_df[Y_FINANCE_PERCENT_CHANGE_COLUMN] = temp_df[Y_FINANCE_CLOSE_COLUMN].pct_change()

      if temp_df is not None:
        time_series_df = pd.concat([time_series_df, temp_df])
        logger.info("fetched %d yfinance ficker data entries for %s ticker", len(temp_df), ticker)
      else:
        logger.warning("failed to fetch yfinance ticker data for %s ticker", ticker)
    return time_series_df.sort_values(by=Y_FINANCE_DATE_COLUMN).reset_index()

  def get_ticker_info(self, ticker):
    """returns ticker information from yFinance API such as open, daylow, dayHigh,  regularMarketPreviousClose, volumne,
    regularMarketPreviousClose, regularMarketChange,regularMarketChangePercent"""
    logger.info("fetching yFinance ticker info for %s", ticker)
    return yf.Ticker(ticker=ticker).info

  def search_news(self, query, article_count):
    """searches market news by query term"""
    logger.info("fetching yFiannce news for query %s, article count %d", query, article_count)
    return yf.Search(query=query, news_count=article_count).news

  def get_sector(self, sector_name):
    """get sector data such as overview, name, research, performance, top companies, top etfs and top mutual funds"""
    logger.info("fetching yFinance sector information for %s sector", sector_name)
    sector_info = yf.Sector(sector_name)
    logger.info("sector_info %s", sector_info)
    return sector_info
