""" Implements portfolio store operations"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import os


from dotenv import load_dotenv
import pandas as pd

from tools.logger import get_logger
from tools.alpha_vantage_client import CLOSE_COLUMN, DATE_KEY, AlphaVantageClient

logger = get_logger(__name__)

load_dotenv()  # Load environment variables from .env file

# ticker,purchase_price,date
PORTFOLIO_PERSISTANCE_CSV = "data/portfolio/portfolio.csv"
TICKER_COLUMN = "ticker"
PURCHASE_PRICE_COLUMN = "purchase_price"
PURCHASE_DATE_COLUMN = "purchase_date"
COST_BASIS_COLUMN = "cost_basis"
RUNNING_TOTAL_COST_COLUMN = "running_total_cost_basis"
SHARES_COLUMN = "shares"
PORTFOLIO_COLUMNS = [TICKER_COLUMN, PURCHASE_DATE_COLUMN, PURCHASE_PRICE_COLUMN,
                     SHARES_COLUMN, COST_BASIS_COLUMN, RUNNING_TOTAL_COST_COLUMN]
TOTAL_CLOSE_COLUMN = "total_close"
RUNNING_SHARES_TOTAL_COLUMN = "running_total_shares"
AVERAGE_COST_COLUMN = "average_cost"
TOTAL_COST_COLUMN = "total_cost_column"
TOTAL_GAIN_LOSS_COLUMN = "total_gain_loss_column"
TERM_COLUMN = "term_column"
MERGE_COLUMN = "_merge"
DAILY_TOTAL_COLUMN = "daily_total"
DATE_FORMAT = "%Y-%m-%d"


class PortfolioStore(ABC):
  """abstract class defining a portfolio store interface"""
  @abstractmethod
  def add_purchase(self, ticker: str, purchase_date: str, purchase_price: float, number_of_shares: int):
    """adds purchase to the portfolio"""

  @abstractmethod
  def import_csv(self, csv_data):
    """imports csv with stock data into the portfolio. CSV must have ticker, purchase_price and date columns"""

  @abstractmethod
  def get_portfolio(self):
    """gets the portfolio dataframe"""


@dataclass
class CSVPortfolioStore(PortfolioStore):
  """implements a portfolio store using a csv file for persistance"""
  df: pd.DataFrame
  portfolio_csv: str

  def __init__(self, portfolio_csv: str = PORTFOLIO_PERSISTANCE_CSV):
    """constructor fo CSV PortfolioStore"""
    self.portfolio_csv = portfolio_csv
    try:
      self.df = pd.read_csv(portfolio_csv).sort_values(by=PURCHASE_DATE_COLUMN).reset_index(drop=True)
      self.df[PURCHASE_DATE_COLUMN] = pd.to_datetime(self.df[PURCHASE_DATE_COLUMN], format=DATE_FORMAT)
      logger.info("Loaded %d purchases from %s", len(self.df), self.portfolio_csv)
    except FileNotFoundError as e:
      logger.warning("Failed to load portfolio file %s. Exception %s", portfolio_csv, e)
      self.df = pd.DataFrame(columns=PORTFOLIO_COLUMNS)

  def add_purchase(self, ticker: str, purchase_date: str, purchase_price: float, number_of_shares: float):
    """Add stock purchase to the portfolio with ticker, purchase date and price"""
    total_cost = purchase_price * number_of_shares
    purchase = {TICKER_COLUMN: [ticker], PURCHASE_DATE_COLUMN: [purchase_date],
                PURCHASE_PRICE_COLUMN: [purchase_price], SHARES_COLUMN: [number_of_shares],
                COST_BASIS_COLUMN: [total_cost]}
    new_row = pd.DataFrame(purchase)
    logger.info("adding new purchase %s to portfolio", purchase)
    self.concat_df_and_save(new_row)

  def import_csv(self, csv_data):
    """import csv data to the portfolio"""
    new_df = pd.read_csv(csv_data)
    new_df[PURCHASE_DATE_COLUMN] = pd.to_datetime(new_df[PURCHASE_DATE_COLUMN], format=DATE_FORMAT)
    new_df = new_df[[TICKER_COLUMN, PURCHASE_DATE_COLUMN, PURCHASE_PRICE_COLUMN, SHARES_COLUMN]]
    logger.info("adding %d new purchases to portfolio", len(new_df))
    self.concat_df_and_save(new_df)

  def update_derived_columns(self):
    """updates derived columns such as running total"""
    self.df[COST_BASIS_COLUMN] = self.df[PURCHASE_PRICE_COLUMN]*self.df[SHARES_COLUMN]

  def concat_df_and_save(self, new_df: pd.DataFrame):
    """concats the new dataframe to the existing dataframe and saves it to file"""
    self.df = pd.concat([self.df, new_df], ignore_index=True)
    self.df[PURCHASE_DATE_COLUMN] = pd.to_datetime(self.df[PURCHASE_DATE_COLUMN], format=DATE_FORMAT)
    self.df = self.df.sort_values(by=PURCHASE_DATE_COLUMN).reset_index(drop=True)
    self.update_derived_columns()
    self.df.to_csv(self.portfolio_csv, index=False)

  def get_portfolio(self):
    """gets the account summary data series"""
    return self.df


@dataclass
class PortfolioManager:
  """portfolio manager used to mange the finance portfolio and alpha vantage api"""
  alpha_vantage_client: AlphaVantageClient
  portfolio_store: CSVPortfolioStore
  last_update_time_series: datetime

  def __init__(self, alpha_vantage_key=os.getenv("ALPHA_VANTAGE_KEY"), portfolio_csv=PORTFOLIO_PERSISTANCE_CSV):
    self.alpha_vantage_client = AlphaVantageClient(api_key=alpha_vantage_key)
    self.portfolio_store = CSVPortfolioStore(portfolio_csv=portfolio_csv)
    self.last_update_time_series = datetime.now()

  def add_purchase(self, ticker: str, purchase_date: str, purchase_price: float, number_of_shares: float):
    """add stock purchase to portfolio"""
    self.portfolio_store.add_purchase(ticker, purchase_date, purchase_price, number_of_shares)

  def import_csv(self, csv_data):
    """import data into the portfolio"""
    self.portfolio_store.import_csv(csv_data)

  def get_time_series_daily(self):
    """gets the latest time_series_daily update for the tickers in the portfolio"""
    self.last_update_time_series = datetime.now()
    portfolio_df = self.portfolio_store.df
    tickers = portfolio_df[TICKER_COLUMN].unique()
    logger.info("portfolio has %d tickers", len(tickers))
    time_series_df = pd.DataFrame()
    for ticker in tickers:
      temp_df = self.alpha_vantage_client.time_series_daily(ticker)
      if temp_df is not None:
        time_series_df = pd.concat([time_series_df, temp_df])
        logger.info("fetched %d time_series_daily entries for %s ticker", len(temp_df), ticker)
      else:
        logger.warning("failed to fetch time_series_daily for %s ticker", ticker)

    return time_series_df

  def get_portfolio(self):
    """get the portfolio"""
    return self.portfolio_store.df

  def get_portfolio_with_running_total_shares(self):
    """gets the portfolio with running total shares by date and ticker"""
    portfolio = self.portfolio_store.df.sort_values(by=[TICKER_COLUMN, PURCHASE_DATE_COLUMN])
    portfolio[RUNNING_SHARES_TOTAL_COLUMN] = portfolio.groupby(TICKER_COLUMN)[SHARES_COLUMN].cumsum()
    return portfolio.reset_index()

  def get_portfolio_summary_df(self):
    """gets the portfolio summary Dataframe by merging the time series daily with portfolio"""
    portfolio_df = self.get_portfolio_with_running_total_shares()
    portfolio_df = portfolio_df.rename(columns={PURCHASE_DATE_COLUMN: DATE_KEY})
    times_series_df = self.get_time_series_daily()
    times_series_df = pd.merge(times_series_df, portfolio_df, on=[TICKER_COLUMN, DATE_KEY], how="outer", indicator=True)
    times_series_df[RUNNING_SHARES_TOTAL_COLUMN] = times_series_df[RUNNING_SHARES_TOTAL_COLUMN].ffill()
    times_series_df = times_series_df.drop(times_series_df[times_series_df[MERGE_COLUMN] == "right_only"].index)
    times_series_df[DAILY_TOTAL_COLUMN] = times_series_df[CLOSE_COLUMN]*times_series_df[RUNNING_SHARES_TOTAL_COLUMN]
    logger.info("fetched portfolio summary with %d time entries", len(times_series_df))
    return times_series_df.reset_index()

  def get_portfolio_positions_df(self):
    """gets the portfolio_positions with todays prices"""
    portfolio_df = self.get_portfolio()
    logger.info("fetched portfolio of size %d", len(portfolio_df))
    time_series_df = self.get_time_series_daily()
    latest_time = time_series_df[DATE_KEY].max()
    logger.info("fected times_series_daily with %d entries and latest time %s", len(time_series_df), latest_time)
    time_series_df = time_series_df[time_series_df[DATE_KEY] == latest_time]
    portfolio_postions_df = pd.merge(portfolio_df, time_series_df, on=[TICKER_COLUMN])
    portfolio_postions_df[TOTAL_COST_COLUMN] = (
      portfolio_postions_df[SHARES_COLUMN] * portfolio_postions_df[PURCHASE_PRICE_COLUMN]
    )
    portfolio_postions_df[TOTAL_GAIN_LOSS_COLUMN] = (
      portfolio_postions_df[SHARES_COLUMN] * portfolio_postions_df[CLOSE_COLUMN] - portfolio_postions_df[TOTAL_COST_COLUMN]
    )
    portfolio_postions_df[TERM_COLUMN] = (
      (portfolio_postions_df[DATE_KEY] - portfolio_postions_df[PURCHASE_DATE_COLUMN])
      .apply(lambda x: "short" if x.days < 365 else "long")
    )
    logger.info("fetched %d portfolio position", len(portfolio_postions_df))
    return portfolio_postions_df.reset_index()
