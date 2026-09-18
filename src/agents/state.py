"""The Graph state that is passed between agents"""
from typing import Annotated, List, Literal, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# route states
FINANCE_FAQ = "finance_faq"
PORTFOLIO_ANALYSIS = "portfolio_analysis"
MARKET_ANALYSIS = "market_analysis"
GOAL_PLANNING = "goal_planning"
ROUTE_STATES = [FINANCE_FAQ, PORTFOLIO_ANALYSIS, MARKET_ANALYSIS, GOAL_PLANNING]

# FinLitState field names
MESSAGES_FIELD = "messages"
USER_INPUT_FIELD = "user_input"
OUTPUT_FIELD = "output"
ROUTE_FIELD = "route"

# graph states for conditional edges
FINANCE_FAQ_TOOLS = "finance_faq_tools"
GRAPH_END = "end"


class FinLitState(TypedDict):
  """class defining the Graph state that can be updated for each node"""
  # conversation history
  messages: Annotated[List[BaseMessage], add_messages]
  # user query
  user_input: str
  # output
  output: str
  # router decision
  route: Literal["finance_faq", "portfolio_analysis", "market_analysis", "goal_planning"]
