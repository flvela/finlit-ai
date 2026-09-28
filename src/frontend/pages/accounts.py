"""Accounts page for FinLit app"""
import altair as alt
import streamlit as st

from tools.alpha_vantage_client import DATE_KEY
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
    portfolio_container.dataframe(portfolio_positions_df)
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
