"""defines the portfolio agent node and prompt"""
from langchain.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime

from agents.common import get_output_state
from agents.context_schema import ContextSchema
from agents.state import (
  GRAPH_END,
  MESSAGES_FIELD,
  PORTFOLIO_AGENT_TOOLS,
  USER_INPUT_FIELD,
  FinLitState
)
from tools.logger import get_logger

PORTFOLIO_AGENT_INSTRUCTIONS = """
You are a portfolio analyzer. Your job is to answer questions about a given users stock or
asset porfolio and perform analysis for risk and value. You have the following tools that you can use for this.
For risk analysis use Sharpe Ratio or Sortino Ratio.

Tools:
1. **get_time_series_daily** - returns the daily OHLCV history (Open, High, Low, Close, Value) for a given ticker
2. **get_global_quote** - get the current open, high, low, price, volumne, latest trading day, previous close,
  change and change percent for a given ticker
3. **get_treasury_yield** - gets the US Treasury(T-BILL) yield daily, weekly and monthly for a given maturity
  timeline (ie. 3month, 10year, etc)
4. **get_ticker_overview** - gets the ticker information including: asset type, industry, sector, exchange,
  currency, description, "PERatio, PEGRATIO, MarketCap, Analysist targets and ratings, Beta, etc...
5. **get_portfolio_summary** - gets the users portfolio that includes ticker,purchase_date,purchase_price,
  shares,daily total value

Output rules:
- provide disclaimer that this analysis is for educational purposes only and user should consult with professional
  analysist before acting on this information
- provide details for steps that were taken to generate the analysis including any calculations performed
- if there is some data missing please state it as missing data and ask user to provide it
- state what formula was used to compute risk
"""

logger = get_logger(__name__)


def portfolio_agent_node(state: FinLitState, runtime: Runtime[ContextSchema]) -> FinLitState:
  """portfolio agent node specializing in answering financial portfolio questions"""
  logger.info("portfolio_agent_node %s", state)

  history = state.get(MESSAGES_FIELD, [])
  system_message = SystemMessage(content=PORTFOLIO_AGENT_INSTRUCTIONS)
  human_message = HumanMessage(content=state[USER_INPUT_FIELD])
  messages = [system_message] + history + [human_message]
  result = runtime.context.portfolio_llm.invoke(messages)

  logger.info("user input %s, llm response %s", human_message.content, result.content)

  return get_output_state(state, result, messages)


def portfolio_agent_should_continue(state: FinLitState) -> str:
  """used to determine if portfolio agent needs another turn. Condition on LangGraph edge"""
  logger.debug("portfolio_agent_should_continue %s", state)

  if MESSAGES_FIELD in state and len(state[MESSAGES_FIELD]) > 0:
    last_msg = state[MESSAGES_FIELD][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
      return PORTFOLIO_AGENT_TOOLS

  return GRAPH_END
