"""defines the finance faq agent for the LangGraph graph"""
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.runtime import Runtime

from agents.state import (
  FINANCE_FAQ_TOOLS,
  GRAPH_END,
  MESSAGES_FIELD,
  OUTPUT_FIELD,
  USER_INPUT_FIELD,
  FinLitState
)
from agents.context_schema import ContextSchema
from tools.logger import get_logger

FINANCE_FAQ_INSTRUCTIONS = """
You are a finance FAQ agent. Your job is to answer querstions regarding general financial knowledge.
You can use the *search_finance_articles* tool to answer questions regarding financial education.

Output rules:
- only answer based on the financial articles found using the tool
- provide the article results from the tool call.
- provide a summary of the articles from the tool.
- provide article URLS that were used to summarize the result
"""

logger = get_logger(__name__)


def finance_faq_node(state: FinLitState, runtime: Runtime[ContextSchema]) -> FinLitState:
  """finance FAQ agent node specializing in answer financial faq questions"""
  logger.debug("financial_faq_node %s", state)

  history = state.get(MESSAGES_FIELD, [])
  system_message = SystemMessage(content=FINANCE_FAQ_INSTRUCTIONS)
  human_message = HumanMessage(content=state[USER_INPUT_FIELD])
  messages = [system_message] + history + [human_message]
  result = runtime.context.financial_faq_llm.invoke(messages)

  logger.info("finance_faq_node user input %s, llm response %s", human_message.content, result.content)
  if result.tool_calls:
    return {MESSAGES_FIELD: [*messages, result] if not state.get(MESSAGES_FIELD) else [result]}

  return {OUTPUT_FIELD: result.content, MESSAGES_FIELD: [AIMessage(content=result.content)]}


def finance_faq_should_continue(state: FinLitState) -> str:
  """used to determine if finance_faq agent needs another turn. Condition on LangGraph edge"""
  logger.debug("finance_faq_should_continue %s", state)

  if MESSAGES_FIELD in state and len(state[MESSAGES_FIELD]) > 0:
    last_msg = state[MESSAGES_FIELD][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
      return FINANCE_FAQ_TOOLS

  return GRAPH_END
