"""Accounts page for FinLit app"""
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

import altair as alt
import streamlit as st
import pandas as pd

from tools.alpha_vantage_client import CLOSE_COLUMN, DATE_KEY
from tools.portfolio import (
  DAILY_TOTAL_COLUMN,
  PURCHASE_DATE_COLUMN,
  PURCHASE_PRICE_COLUMN,
  SHARES_COLUMN,
  TERM_COLUMN,
  TICKER_COLUMN,
  TOTAL_COST_COLUMN,
  TOTAL_GAIN_LOSS_COLUMN,
  PortfolioManager
)
from frontend.utils.common import PORTFOLIO_MANAGER_CONFIG

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
ASSET_TYPE_KEY = "AssetType"
INDUSTRY_KEY = "Industry"
SECTOR_KEY = "Sector"
EXCHANGE_KEY = "Exchange"
CURRENCY_KEY = "Currency"
ADDRESS_KEY = "Address"
DESCRIPTION_KEY = "Description"

# news sentiment response keys
FEED_KEY = "Feed"


@st.dialog("Add Purchase")
def add_purchase():
  """creates a dialog to add a purchase to the portfolio"""
  ticker = st.text_input(TICKER_INPUT)
  purchase_date = st.date_input(PURCHASE_DATE_INPUT, format="YYYY-MM-DD")
  purchase_price = st.text_input(PURCHASE_PRICE_INPUT,
                                 validate=(PURCHASE_FLOAT_REGEX, "Price should be of format 123.45"))
  purchase_amount = st.text_input(PURCHASE_AMOUNT_INPUT,
                                  validate=(PURCHASE_FLOAT_REGEX, "Amount should be of format 123.45"))
  if st.button("Add Purchase"):
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
    account_summary_container.dataframe(portfolio_summary_df)
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

    treasury_yield = portfolio_manager.get_treasury_yield("10year", "monthly")
    if "data" in treasury_yield:
      treasury_yield_df = pd.DataFrame(portfolio_manager.get_treasury_yield("10year", "monthly")["data"])
      account_summary_container.write("Treasury Yield 10 year")
      three_months_ago = date.today() - relativedelta(month=3)
      account_summary_container.write(three_months_ago)
      treasury_yield_df = treasury_yield_df[treasury_yield_df["date"] > str(three_months_ago)]
      account_summary_container.dataframe(treasury_yield_df)
      account_summary_container.line_chart(treasury_yield_df, x="date", y="value", x_label=DATE_LABEL, y_label="% Yield")
    else:
      account_summary_container.warning("Treasury yield not available")
      account_summary_container.warning(treasury_yield)

  else:
    st.badge(label="Add purchases to see account summary and insights", color="blue", icon=":material/info:")


def create_quote_container(quote_data):
  """creates a quote container"""
  col1, col2 = st.columns(2)
  col1.markdown("**Quote**")
  col2.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
  st.markdown(f"**{quote_data[QUOTE_KEY]}**")
  col1, col2 = st.columns(2)
  col1.write("Day Range")
  col2.slider("Day Range",
              min_value=float(quote_data[LOW_KEY]),
              max_value=float(quote_data[HIGH_KEY]),
              value=float(quote_data[QUOTE_KEY]),
              label_visibility="collapsed",
              disabled=True)

  quote_table_data = {
    "Open": float(quote_data[OPEN_KEY]),
    "High": float(quote_data[HIGH_KEY]),
    "Low": float(quote_data[LOW_KEY]),
    "Volume": float(quote_data[VOLUMNE_KEY]),
    "Previous Trading Day":  quote_data[PREVIOUS_DATE_KEY],
    "Previous Trading Close": float(quote_data[PREVIOUS_CLOSE_KEY]),
    "Change": float(quote_data[CHANGE_KEY]),
    "Change %": quote_data[CHANGE_PERCENT_KEY],
  }
  st.table(quote_table_data, border="horizontal")


def create_overview_container(overview_data):
  """creates the overview container"""
  st.markdown("**Overview**")
  if ASSET_TYPE_KEY not in overview_data:
    st.warning("Overview data not available")
    st.warning(overview_data)
  else:
    col_data = [
      ("Asset Type", overview_data[ASSET_TYPE_KEY]),
      ("Industry", overview_data[INDUSTRY_KEY]),
      ("Sector", overview_data[SECTOR_KEY]),
      ("Exchange", overview_data[EXCHANGE_KEY]),
      ("Currency", overview_data[CURRENCY_KEY]),
      ("Location", overview_data[ADDRESS_KEY])
    ]
    st.table(col_data, border="horizontal")
    st.write(overview_data[DESCRIPTION_KEY])


def create_news_feed_container(news_sentiment_data):
  """creates the news feed container"""
  st.markdown("**News**")
  if FEED_KEY in news_sentiment_data:
    st.dataframe(news_sentiment_data[FEED_KEY])
  else:
    st.warning("News Sentiment data not available")
    st.warning(news_sentiment_data)


def create_chart_container(time_series_daily, quote_data):
  """creates the quote container"""
  time_series_daily = time_series_daily.groupby([DATE_KEY])[CLOSE_COLUMN].sum().reset_index()
  time_series_daily = time_series_daily.rename(columns={CLOSE_COLUMN: DAILY_TOTAL_COLUMN})
  todays_row = pd.DataFrame([
    {DAILY_TOTAL_COLUMN: quote_data[QUOTE_KEY], DATE_KEY: datetime.now()}])
  time_series_daily = pd.concat([time_series_daily, todays_row], ignore_index=True)
  st.dataframe(time_series_daily)
  chart = (
      alt.Chart(time_series_daily)
      .mark_line(point=True)
      .encode(
        x=alt.X(ALTAIR_DATE_COLUMN, axis=alt.Axis(format='%b %d', title=DATE_LABEL)),
        y=alt.Y(ALTAIR_TOTAL_COLUMN, axis=alt.Axis(format="$,.2f", title=TOTAL_LABEL)),
        tooltip=[
          alt.Tooltip(ALTAIR_DATE_COLUMN, title=DATE_LABEL),
          alt.Tooltip(ALTAIR_CLOSE_COLUMN, title=TOTAL_LABEL)
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
    create_overview_container(portfolio_manager.get_overview(ticker))
  with news_sentiment_col:
    create_news_feed_container(portfolio_manager.get_news_sentiment(ticker))

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


def accounts_page():
  """displays the account page"""
  st.header("Accounts & Trade", text_alignment="center")
  st.set_page_config(layout="wide")

  if PORTFOLIO_MANAGER_CONFIG not in st.session_state:
    st.session_state[PORTFOLIO_MANAGER_CONFIG] = PortfolioManager()

  left, right, _ = st.columns([1, 1, 10], gap="xxsmall")
  if left.button("Add Purchase"):
    add_purchase()
  if right.button("Import CSV"):
    import_csv()

  summary_tab, portfolio_tab, _ = st.tabs([SUMMARY_TAB, POSITIONS_TAB, ANALYSIS_TAB])

  with summary_tab:
    show_summary_tab()
  with portfolio_tab:
    show_portfolio_tab()


accounts_page()
