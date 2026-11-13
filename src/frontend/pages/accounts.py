"""Accounts page for FinLit app"""
from datetime import datetime

import streamlit as st
import pandas as pd
import altair as alt

from frontend.components.common import create_news_feed_df_container
from frontend.components.ui_config import configure_application
from frontend.utils.common import (
  CONFIG_ERROR_MESSAGE,
  FINLIT_ASSISTANT_CONFIG,
  MARKET_MANAGER_CONFIG,
  PORTFOLIO_ANALYSIS_RESULT_CONFIG,
  PORTFOLIO_MANAGER_CONFIG,
  config_missing_message,
  is_config_complete
)
from tools.alpha_vantage_client import CLOSE_COLUMN, DATE_KEY
from tools.portfolio_manager import (
  DAILY_TOTAL_COLUMN,
  PURCHASE_DATE_COLUMN,
  PURCHASE_PRICE_COLUMN,
  SHARES_COLUMN,
  TERM_COLUMN,
  TICKER_COLUMN,
  TOTAL_COST_COLUMN,
  TOTAL_GAIN_LOSS_COLUMN
)

SUMMARY_TAB = "Summary"
POSITIONS_TAB = "Positions"
ANALYSIS_TAB = "Analysis"
PURCHASE_HISTORY_TAB = "Purchase History"
RESEARCH_TAB = "Research"

TICKER_INPUT = "Ticker"
PURCHASE_DATE_INPUT = "Purchase Date"
PURCHASE_PRICE_INPUT = "Purchase Price"
PURCHASE_AMOUNT_INPUT = "Purchase Amount"
PORTFOLIO_CSV_INPUT = "Select Portfolio csv to import"

DATE_LABEL = "Date"
TOTAL_LABEL = "Total"
PRICE_LABEL = "Price"

PURCHASE_FLOAT_REGEX = r"^\d+\.\d+$"
FORMATTED_DATE_COLUMN = "formatted_date"
ALTAIR_DATE_COLUMN = f'{DATE_KEY}:T'
ALTAIR_TOTAL_COLUMN = f'{DAILY_TOTAL_COLUMN}:Q'
ALTAIR_CLOSE_COLUMN = f'{CLOSE_COLUMN}:Q'

# Global quote response keys
QUOTE_KEY = "05. price"
OPEN_KEY = "02. open"
HIGH_KEY = "03. high"
LOW_KEY = "04. low"
VOLUMNE_KEY = "06. volume"
PREVIOUS_DATE_KEY = "07. latest trading day"
PREVIOUS_CLOSE_KEY = "08. previous close"
CHANGE_KEY = "09. change"
CHANGE_PERCENT_KEY = "10. change percent"

# overview response keys
ASSET_TYPE_KEY = "quoteType"
INDUSTRY_KEY = "industry"
SECTOR_KEY = "sector"
EXCHANGE_KEY = "exchange"
CURRENCY_KEY = "currency"
CITY_KEY = "city"
STATE_KEY = "state"
COUNTRY_KEY = "country"
DESCRIPTION_KEY = "longBusinessSummary"


ADD_PURCHASE_BUTTON = ":material/add: Purchase"
UPLOAD_CSV_BUTTON = ":material/upload_file: CSV"


@st.dialog("Add Purchase")
def add_purchase():
  """creates a dialog to add a purchase to the portfolio"""
  ticker = st.text_input(TICKER_INPUT)
  purchase_date = st.date_input(PURCHASE_DATE_INPUT, format="YYYY-MM-DD")
  purchase_price = st.text_input(PURCHASE_PRICE_INPUT,
                                 validate=(PURCHASE_FLOAT_REGEX, "Price should be of format 123.45"))
  purchase_amount = st.text_input(PURCHASE_AMOUNT_INPUT,
                                  validate=(PURCHASE_FLOAT_REGEX, "Amount should be of format 123.45"))
  if st.button(ADD_PURCHASE_BUTTON):
    st.session_state[PORTFOLIO_MANAGER_CONFIG].add_purchase(ticker, purchase_date,
                                                            float(purchase_price), float(purchase_amount))
    st.rerun()


@st.dialog("Import CSV file")
def import_csv():
  """creates a dialog to import a csv file with an investment portfolio"""
  csv_file = st.file_uploader(PORTFOLIO_CSV_INPUT, type="csv")
  if csv_file:
    st.session_state[PORTFOLIO_MANAGER_CONFIG].import_csv(csv_file)
    st.rerun()


def show_summary_tab():
  """show the summary tab"""
  portfolio_manager = st.session_state[PORTFOLIO_MANAGER_CONFIG]
  portfolio = portfolio_manager.get_portfolio()
  if len(portfolio) > 0:
    account_summary_container = st.container()
    account_summary_container.write("Account Summary")

    portfolio_summary_df = portfolio_manager.get_portfolio_summary_df()
    portfolio_summary_df = portfolio_summary_df.groupby([DATE_KEY])[DAILY_TOTAL_COLUMN].sum().reset_index()
    chart = (
        alt.Chart(portfolio_summary_df)
        .mark_line(point=True)
        .encode(
          x=alt.X(ALTAIR_DATE_COLUMN, axis=alt.Axis(format='%b %d', title=DATE_LABEL)),
          y=alt.Y(ALTAIR_TOTAL_COLUMN, axis=alt.Axis(format="$,.2f", title=TOTAL_LABEL)),
          tooltip=[
            alt.Tooltip(ALTAIR_DATE_COLUMN, title=DATE_LABEL),
            alt.Tooltip(ALTAIR_TOTAL_COLUMN, title=TOTAL_LABEL)
          ]
        )
    )
    account_summary_container.altair_chart(chart)

  else:
    st.badge(label="Add purchases to see account summary and insights", color="blue", icon=":material/info:")


def create_quote_container(quote_data):
  """creates a quote container"""
  st.markdown("**Quote**")
  if QUOTE_KEY not in quote_data:
    st.warning("Quote data not available")
    st.warning(quote_data)
  else:
    st.slider("Quote",
              min_value=float(quote_data[LOW_KEY]),
              max_value=float(quote_data[HIGH_KEY]),
              value=float(quote_data[QUOTE_KEY]),
              label_visibility="collapsed",
              disabled=True)

    change_icon = ":material/trending_up:" if float(quote_data[CHANGE_KEY]) > 0 else ":material/trending_down:"

    quote_table_data = {
      ":material/calendar_month: Date": datetime.now().strftime("%b %d, %Y"),
      ":material/sell: Price": float(quote_data[QUOTE_KEY]),
      ":material/arrow_forward: Open": float(quote_data[OPEN_KEY]),
      ":material/vertical_align_top: High": float(quote_data[HIGH_KEY]),
      ":material/vertical_align_bottom: Low": float(quote_data[LOW_KEY]),
      ":material/functions: Volume": float(quote_data[VOLUMNE_KEY]),
      ":material/calendar_month: Previous Trading Day":  quote_data[PREVIOUS_DATE_KEY],
      ":material/sell: Previous Trading Close": float(quote_data[PREVIOUS_CLOSE_KEY]),
      f"{change_icon} Change": float(quote_data[CHANGE_KEY]),
      f"{change_icon} Change %": quote_data[CHANGE_PERCENT_KEY],
    }
    st.table(quote_table_data, border="horizontal")


def create_overview_container(ticker):
  """creates the overview container"""
  market_manager = st.session_state[MARKET_MANAGER_CONFIG]
  ticker_info = market_manager.get_ticker_info(ticker)
  st.markdown("**Overview**")
  if ASSET_TYPE_KEY not in ticker_info:
    st.warning("Overview data not available")
    st.warning(ticker_info)
  else:
    location = f"{ticker_info[CITY_KEY]}, {ticker_info[STATE_KEY]}, {ticker_info[COUNTRY_KEY]}"
    col_data = [
      ("Asset Type", ticker_info[ASSET_TYPE_KEY]),
      ("Industry", ticker_info[INDUSTRY_KEY]),
      ("Sector", ticker_info[SECTOR_KEY]),
      ("Exchange", ticker_info[EXCHANGE_KEY]),
      ("Currency", ticker_info[CURRENCY_KEY]),
      ("Location", location)
    ]
    st.table(col_data, border="horizontal")
    st.write(ticker_info[DESCRIPTION_KEY])


def create_news_feed_container(ticker):
  """creates the news feed container"""
  st.markdown("**News**")
  market_manager = st.session_state[MARKET_MANAGER_CONFIG]
  news = market_manager.search_news(ticker, 100)
  if news is not None and len(news) > 0:
    create_news_feed_df_container(pd.DataFrame(news), news_per_page=5, unique_key=ticker)
  else:
    st.warning("News data not available")
    st.warning(news)


def create_chart_container(time_series_daily, quote_data):
  """creates the chart container"""
  st.markdown("**Chart**")
  time_series_daily = time_series_daily.groupby([DATE_KEY])[CLOSE_COLUMN].sum().reset_index()
  time_series_daily = time_series_daily.rename(columns={CLOSE_COLUMN: DAILY_TOTAL_COLUMN})
  todays_row = pd.DataFrame([
    {DAILY_TOTAL_COLUMN: quote_data[QUOTE_KEY], DATE_KEY: datetime.now()}])
  time_series_daily = pd.concat([time_series_daily, todays_row], ignore_index=True)

  chart = (
      alt.Chart(time_series_daily)
      .mark_line(point=True)
      .encode(
        x=alt.X(ALTAIR_DATE_COLUMN, axis=alt.Axis(format='%b %d', title=DATE_LABEL)),
        y=alt.Y(ALTAIR_TOTAL_COLUMN, axis=alt.Axis(format="$,.2f", title=PRICE_LABEL)),
        tooltip=[
          alt.Tooltip(ALTAIR_DATE_COLUMN, title=DATE_LABEL),
          alt.Tooltip(ALTAIR_TOTAL_COLUMN, title=PRICE_LABEL)
        ]
      )
  )
  st.altair_chart(chart)


def show_portfolio_item_details_expander(portfolio_manager, portfolio_positions_df, ticker):
  """used the given portfolio container to display portfolio item details"""
  purchase_history, research = st.tabs([PURCHASE_HISTORY_TAB, RESEARCH_TAB])
  purchase_history.dataframe(portfolio_positions_df[portfolio_positions_df[TICKER_COLUMN] == ticker])
  quote_col, chart_col = research.columns(2, border=True)
  global_qoute = portfolio_manager.get_global_quote(ticker)
  with quote_col:
    create_quote_container(global_qoute)
  with chart_col:
    create_chart_container(portfolio_manager.get_time_series_daily(ticker), global_qoute)
  overview_col, news_sentiment_col = research.columns(2, border=True)
  with overview_col:
    create_overview_container(ticker)
  with news_sentiment_col:
    create_news_feed_container(ticker)


def show_portfolio_tab():
  """show the portfolio tab"""
  portfolio_manager = st.session_state[PORTFOLIO_MANAGER_CONFIG]
  portfolio = portfolio_manager.get_portfolio()
  if len(portfolio) > 0:
    portfolio_container = st.container()
    portfolio_positions_df = portfolio_manager.get_portfolio_positions_df()
    display_columns = [TICKER_COLUMN, SHARES_COLUMN, PURCHASE_DATE_COLUMN, PURCHASE_PRICE_COLUMN,
                       TOTAL_COST_COLUMN, TOTAL_GAIN_LOSS_COLUMN, TERM_COLUMN]
    portfolio_positions_df = portfolio_positions_df[display_columns].sort_values(
      by=[TICKER_COLUMN, PURCHASE_DATE_COLUMN], ascending=[True, False]
    )
    output_df = portfolio_positions_df.groupby(TICKER_COLUMN)[[TOTAL_GAIN_LOSS_COLUMN]].sum().reset_index()
    for _, row in output_df.iterrows():
      ticker = row[TICKER_COLUMN]
      logo = portfolio_manager.get_company_logo(ticker)
      logo = f"![Icon]({logo})" if logo is not None else ""

      with portfolio_container.expander(f"{logo} {ticker}\t{row[TOTAL_GAIN_LOSS_COLUMN]:+.2f}"):
        show_portfolio_item_details_expander(portfolio_manager, portfolio_positions_df, ticker)
  else:
    st.badge(label="Add purchases to see account summary and insights", color="blue", icon=":material/info:")


def show_analysis_tab():
  """show the analysis tab"""
  st.info(":material/info: Portfolio Analysis will perform an AI-assisted analysis of your current positions."
          "Analysis is for informational and educational purposes and should not replace expert financial advice."
          "\n Please consult with a financial expert before making any trade decisions based on this analysis")
  if st.button(":material/search_insights: Analyze Portfolio"):
    assistant = st.session_state[FINLIT_ASSISTANT_CONFIG]
    assistant.reset()
    prompt = "analyze Portfolio"
    with st.status(":material/search_insights: Peforming Analysis") as status:
      st.session_state[PORTFOLIO_ANALYSIS_RESULT_CONFIG] = assistant.ask(prompt)
      status.update(label="Analysis Complete", state="complete")

  result_placeholder = st.empty()

  if (PORTFOLIO_ANALYSIS_RESULT_CONFIG in st.session_state
      and st.session_state[PORTFOLIO_ANALYSIS_RESULT_CONFIG] is not None):
    result_placeholder.markdown(st.session_state[PORTFOLIO_ANALYSIS_RESULT_CONFIG])
  else:
    result_placeholder.markdown("")


def accounts_page():
  """displays the account page"""
  st.header("Accounts & Trade", text_alignment="center")
  st.set_page_config(layout="wide")

  if is_config_complete():
    if PORTFOLIO_MANAGER_CONFIG not in st.session_state:
      configure_application()

    left, right, _ = st.columns([1, 1, 10], gap="xxsmall")
    if left.button(ADD_PURCHASE_BUTTON):
      add_purchase()
    if right.button(UPLOAD_CSV_BUTTON):
      import_csv()

    summary_tab, portfolio_tab, analysis_tab = st.tabs([SUMMARY_TAB, POSITIONS_TAB, ANALYSIS_TAB])

    with summary_tab:
      show_summary_tab()
    with portfolio_tab:
      show_portfolio_tab()
    with analysis_tab:
      show_analysis_tab()
  else:
    if CONFIG_ERROR_MESSAGE in st.session_state:
      st.error(st.session_state[CONFIG_ERROR_MESSAGE])
    st.warning(f"Please configure your application in sidebar. {config_missing_message()}")


accounts_page()
