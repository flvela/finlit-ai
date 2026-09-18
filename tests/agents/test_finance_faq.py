"""Unit tests for Finance FAQ Agent"""
import pytest

from langchain.messages import AIMessage, ToolCall

from agents.finance_faq import finance_faq_node, finance_faq_should_continue
from agents.state import (
  FINANCE_FAQ_TOOLS,
  GRAPH_END,
  MESSAGES_FIELD,
  USER_INPUT_FIELD,
  FinLitState
)
from testutils.common import init_test_runtime
from tools.logger import get_logger

test_data = [
  # user input and true/false if we should call tools
  ("Tell me the difference between RSU and ESPP", True),
  ("what should I buy today", False)
]

logger = get_logger(__name__)


@pytest.mark.parametrize("user_input, has_tool_calls", test_data)
def test_finance_faq_node(user_input: str, has_tool_calls: bool):
  """unit test for finance_faq_node"""
  state = FinLitState()
  state[USER_INPUT_FIELD] = user_input
  result = finance_faq_node(state, init_test_runtime())
  logger.info("result %s", result)
  if has_tool_calls:
    assert len(result[MESSAGES_FIELD]) > 0
    assert hasattr(result[MESSAGES_FIELD][-1], "tool_calls")
    tool_calls = result[MESSAGES_FIELD][-1].tool_calls
    assert len(tool_calls) > 0
  else:
    assert len(result[MESSAGES_FIELD]) > 0


tool_call = ToolCall({"name": "foo", "args": {"a": 1}, "id": "123"})

test_state_data = [
  ({}, GRAPH_END),
  ({MESSAGES_FIELD: [AIMessage(content="", tool_calls=[tool_call])]}, FINANCE_FAQ_TOOLS),
  ({MESSAGES_FIELD: []}, GRAPH_END),
  ({MESSAGES_FIELD: [{"content", "any_content"}]}, GRAPH_END)
]


@pytest.mark.parametrize("state, expected_output", test_state_data)
def test_finance_faq_should_continue(state, expected_output):
  """finance_faq_should_continue unit test"""
  result = finance_faq_should_continue(state)
  assert expected_output == result
