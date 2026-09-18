"""defines the router agent for the LangGraph graph"""
from langchain.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime

from agents.state import MESSAGES_FIELD, ROUTE_FIELD, USER_INPUT_FIELD, FinLitState
from agents.context_schema import ContextSchema


ROUTER_INSTRUCTIONS = """
  You are a router agent and your job is to clasify the user's reques.
  Here are the different routing options:
  1. if user wants to learn about financial terms or is asking general finance question respond with: finance_faq
  2. if user wants to analyze their stock portfolio respond with: portfolio_analysis
  3. if user wants to analyze the general financial markets and not their specific portfolio respond with: market_analysis
  4. if user wants to create or modify a financial goal respond with: goal_planning

  Respond with only one word: either finance_faq, portfolio_analysis, market_analysis or goal_planning
"""


def router_node(state: FinLitState, runtime: Runtime[ContextSchema]) -> FinLitState:
  """router agent node that decides how to route the user query to a downstream agent"""
  history = state.get(MESSAGES_FIELD, [])[-3:]
  messages = [
    SystemMessage(content=ROUTER_INSTRUCTIONS),
    *history,
    HumanMessage(content=state[USER_INPUT_FIELD])
  ]
  result = runtime.context.llm.invoke(messages)
  return {ROUTE_FIELD: result.content, MESSAGES_FIELD: [HumanMessage(content=state[USER_INPUT_FIELD])]}


def route_decision(state: FinLitState) -> str:
  """returns the route decision based on the given graph state"""
  return state[ROUTE_FIELD]
