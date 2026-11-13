"""defines the market analysis agent node and prompt"""
from langchain.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime

from agents.common import get_output_state
from agents.context_schema import ContextSchema
from agents.state import (
  GRAPH_END,
  MESSAGES_FIELD,
  MARKET_ANALYSIS_TOOLS,
  USER_INPUT_FIELD,
  FinLitState
)
from tools.logger import get_logger

MARKET_ANALYSIS_AGENT_INSTRUCTIONS = """
You are a US financial market analyzer. Your job is to report on financial market
indices such as S&P 500, Nasdaq Composite and Dow Jones Index, 10 year US Treasury bill and
brent crude oil. You can also investigate different market sectors "basic-materials", "communication-services",
"consumer-cyclical", "consumer-defensive", "energy", "financial-services", "healthcare", "industrials", "real-estate",
"technology", "utilities".
You can search financial market news and provide company/ticker overview and research

Tools:
1. **get_ticker_overview** - gets the ticker information including: asset type, industry, sector, exchange,
  currency, description, "PERatio, PEGRATIO, MarketCap, Analysist targets and ratings, Beta, etc...
2. **get_us_market_indices** - get the us market indices S&P500, NASDAQ, Dow Jones
3. **search_finance_market_news** - search financial market news by query term and article count
4. **get_us_finance_sector_data** - get sector data such as overview, name, research, performance, top companies,
  ETFs and mutual funds

Output Rules:
- provide disclaimer that this analysis is for educational purposes only and user should consult with professional
  analysist before acting on this information
- for how US markets are doing question report S&P 500, Nasdaq Composite, Dow Jones Index, 10 year US Treasury bill 
  and brent crude oil daily percentage change only
- for 10 year TBill data use get_ticker_overview and ticker ^TNX
- for brent crude oil data use get_ticker_overview and ticker BZ=F
"""

logger = get_logger(__name__)


def market_analysis_agent_node(state: FinLitState, runtime: Runtime[ContextSchema]) -> FinLitState:
  """market analysis agent node specializing in answering US financial market analysis questions"""
  logger.info("market_analysis_agent_node %s", state)

  history = state.get(MESSAGES_FIELD, [])
  system_message = SystemMessage(content=MARKET_ANALYSIS_AGENT_INSTRUCTIONS)
  human_message = HumanMessage(content=state[USER_INPUT_FIELD])
  messages = [system_message] + history + [human_message]
  result = runtime.context.llms.market_analysis_llm.invoke(messages)

  logger.info("user input %s, llm response %s", human_message.content, result.content)

  return get_output_state(state, result, messages)


def market_analysis_agent_should_continue(state: FinLitState) -> str:
  """used to determine if market analysis agent needs another turn. Condition on LangGraph edge"""
  logger.debug("market_analysis_agent_should_continue %s", state)

  if MESSAGES_FIELD in state and len(state[MESSAGES_FIELD]) > 0:
    last_msg = state[MESSAGES_FIELD][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
      return MARKET_ANALYSIS_TOOLS

  return GRAPH_END
