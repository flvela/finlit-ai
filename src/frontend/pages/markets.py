"""Defines the Markets Page for the streamlit application"""
from datetime import datetime

import streamlit as st
from streamlit.delta_generator import DeltaGenerator
import pandas as pd
import altair as alt

from frontend.components.common import create_news_feed_df_container
from frontend.components.ui_config import configure_application
from frontend.utils.common import (
  CONFIG_ERROR_MESSAGE,
  MARKET_MANAGER_CONFIG,
  config_missing_message,
  is_config_complete
)
from tools.market_manager import (
  Y_FINANCE_DATE_COLUMN,
  Y_FINANCE_PERCENT_CHANGE_COLUMN,
  Y_FINANCE_SECTORS,
  Y_FINANCE_TICKER_INFO_DISPLAY_NAME,
  Y_FINANCE_TICKER_NAME_COLUMN,
  Y_FINANCE_TICKER_INFO_REGULAR_MARKET_CHANGE,
  Y_FINANCE_TICKER_INFO_REGULAR_MARKET_CHANGE_PERCENT,
  Y_FINANCE_TICKER_INFO_REGULAR_MARKET_PRICE,
  Y_FINANCE_TICKER_INFO_REGULAR_MARKET_TIME,
  Y_FINANCE_TICKER_INFO_SHORT_NAME
)

US_INDICES_LABEL = "US Indices"
US_MARKETS_NEWS_LABEL = "US Market News"
US_SECTOR_PERFORMANCE_LABEL = "US Sector Performance"
DOW_JONES_TICKER = "^DJI"
NASDAQ_TICKER = "^IXIC"
SP500_TICKER = "^GSPC"
TREASURY_YIELD_TICKER = "^TNX"
BRENT_CRUDE_TICKER = "BZ=F"

UUID_NEWS_KEY = "uuid"
PROVIDER_PUBLISH_TIME_NEWS_KEY = "providerPublishTime"
PERCENT_CHANGE_KEY = "Percent_Change"

ALTAIR_DATE_COLUMN = f'{Y_FINANCE_DATE_COLUMN}:T'
ALTAIR_PRICE_COLUMN = f'{Y_FINANCE_PERCENT_CHANGE_COLUMN}:Q'
ALTAIR_TICKER_COLUMN = f'{Y_FINANCE_TICKER_NAME_COLUMN}:N'
ALTAIR_DATE_LABEL = "Date"
ALTAIR_PRICE_LABEL = "Price"


def show_index_col(idx: str, container: DeltaGenerator):
  """show the index column populated with market price, price change and change percentage"""
  market_manager = st.session_state[MARKET_MANAGER_CONFIG]
  ticker_info = market_manager.get_ticker_info(idx)
  ticker_name = ticker_info[Y_FINANCE_TICKER_INFO_SHORT_NAME]
  ticker_price = ticker_info[Y_FINANCE_TICKER_INFO_REGULAR_MARKET_PRICE]
  ticker_price_change = ticker_info[Y_FINANCE_TICKER_INFO_REGULAR_MARKET_CHANGE]
  ticker_price_change_percent = ticker_info[Y_FINANCE_TICKER_INFO_REGULAR_MARKET_CHANGE_PERCENT]
  ticker_market_date = datetime.fromtimestamp(ticker_info[Y_FINANCE_TICKER_INFO_REGULAR_MARKET_TIME])
  delta_label = f"{ticker_price_change:+.2f} ({ticker_price_change_percent:+.2f}%)"
  formatted_date = ticker_market_date.strftime("%Y-%m-%d %H:%M:%S")
  date_label = f"Last updated: {formatted_date}"
  container.metric(label=ticker_name, value=ticker_price, delta=delta_label)
  container.write(date_label)


def show_markets_container():
  """shows the markets container"""
  with st.container(border=True):
    st.write(US_INDICES_LABEL)
    market_manager = st.session_state[MARKET_MANAGER_CONFIG]
    us_market_indices_df = market_manager.get_us_market_indices_df()
    djia_col, nasdaq_col, sp_500_col = st.columns(3, border=True)
    show_index_col(DOW_JONES_TICKER, djia_col)
    show_index_col(NASDAQ_TICKER, nasdaq_col)
    show_index_col(SP500_TICKER, sp_500_col)
    num_days_to_show = 30
    end_idx = len(us_market_indices_df)
    start_idx = end_idx - num_days_to_show

    chart = (
      alt.Chart(us_market_indices_df.iloc[start_idx: end_idx])
      .mark_line(point=True)
      .encode(
          x=alt.X(ALTAIR_DATE_COLUMN, axis=alt.Axis(format='%b %d', title=ALTAIR_DATE_LABEL)),
          y=alt.Y(ALTAIR_PRICE_COLUMN, axis=alt.Axis(format=".2%", title=ALTAIR_PRICE_LABEL)),
          color=ALTAIR_TICKER_COLUMN,
          tooltip=[
            alt.Tooltip(ALTAIR_DATE_COLUMN, title=ALTAIR_DATE_LABEL, format='%b %d'),
            alt.Tooltip(ALTAIR_PRICE_COLUMN, title=ALTAIR_PRICE_LABEL, format=".2%")
          ]
        )
    )
    st.altair_chart(chart)


def show_tbill_and_oil_container():
  """show performance of 10-year US treasury bill and brent crude oil"""
  t_bill_col, oil_col = st.columns(2, border=True)
  show_index_col(TREASURY_YIELD_TICKER, t_bill_col)
  show_index_col(BRENT_CRUDE_TICKER, oil_col)


def show_news_container():
  """Shows the market news container"""
  with st.container(border=True):
    st.write(US_MARKETS_NEWS_LABEL)
    market_manager = st.session_state[MARKET_MANAGER_CONFIG]
    dow_news = pd.DataFrame(market_manager.search_news(DOW_JONES_TICKER, 100))
    nasdaq_news = pd.DataFrame(market_manager.search_news(NASDAQ_TICKER, 100))
    sp500_news = pd.DataFrame(market_manager.search_news(SP500_TICKER, 100))
    news = (pd.concat([dow_news, nasdaq_news, sp500_news])
            .drop_duplicates(subset=[UUID_NEWS_KEY])
            .sort_values(by=PROVIDER_PUBLISH_TIME_NEWS_KEY, ascending=False)
            .reset_index())
    create_news_feed_df_container(pd.DataFrame(news), news_per_page=5, unique_key="us_market")


def show_sector_performance(sector_name):
  """show the sector performance"""
  market_manager = st.session_state[MARKET_MANAGER_CONFIG]
  ticker_info = market_manager.get_sector(sector_name).ticker.info
  name_col, change_col = st.columns(2)
  name_col.write(ticker_info[Y_FINANCE_TICKER_INFO_DISPLAY_NAME])
  ticker_price_change_percent = ticker_info[Y_FINANCE_TICKER_INFO_REGULAR_MARKET_CHANGE_PERCENT]
  color = "green" if ticker_price_change_percent > 0 else "red"
  icon = "arrow_upward" if ticker_price_change_percent > 0 else "arrow_downward"
  with change_col:
    st.badge(f"{ticker_price_change_percent:.2f}%", icon=f":material/{icon}:", color=color)


def show_sector_information_container():
  """Shows the sector container for US stocks"""
  with st.container(border=True):
    st.write(US_SECTOR_PERFORMANCE_LABEL)
    for sector in Y_FINANCE_SECTORS:
      show_sector_performance(sector)


def markets_page():
  """displays the account page"""
  st.header("Markets", text_alignment="center")
  st.set_page_config(layout="wide")
  if is_config_complete():
    if MARKET_MANAGER_CONFIG not in st.session_state:
      configure_application()

    show_markets_container()
    show_news_container()
    show_tbill_and_oil_container()
    show_sector_information_container()
  else:
    if CONFIG_ERROR_MESSAGE in st.session_state:
      st.error(st.session_state[CONFIG_ERROR_MESSAGE])
    st.warning(f"Please configure your application in sidebar. {config_missing_message()}")


markets_page()
