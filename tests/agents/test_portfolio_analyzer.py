"""Unit tests for Finance FAQ Agent"""
import pytest

from langchain.messages import AIMessage, ToolCall

from agents.portfolio_analyzer import portfolio_agent_node, portfolio_agent_should_continue
from agents.state import (
  PORTFOLIO_AGENT_TOOLS,
  GRAPH_END,
  MESSAGES_FIELD,
  USER_INPUT_FIELD,
  FinLitState
)
from testutils.common import assert_agent_node_output_state, init_test_runtime
from tools.logger import get_logger

test_data = [
  # user input and true/false if we should call tools
  ("what is my portfolio summary", True),
  ("what is the overview for IBM", True),
  ("perform portfolio analysis for my portfolio and make suggests to reduce risk", True)
]

logger = get_logger(__name__)


@pytest.mark.parametrize("user_input, has_tool_calls", test_data)
def test_portfolio_agent_node(user_input: str, has_tool_calls: bool):
  """unit test for portfolio_agent_node"""
  state = FinLitState()
  state[USER_INPUT_FIELD] = user_input
  result = portfolio_agent_node(state, init_test_runtime())
  assert_agent_node_output_state(result, has_tool_calls)


tool_call = ToolCall({"name": "foo", "args": {"a": 1}, "id": "123"})

test_state_data = [
  ({}, GRAPH_END),
  ({MESSAGES_FIELD: [AIMessage(content="", tool_calls=[tool_call])]}, PORTFOLIO_AGENT_TOOLS),
  ({MESSAGES_FIELD: []}, GRAPH_END),
  ({MESSAGES_FIELD: [{"content", "any_content"}]}, GRAPH_END)
]


@pytest.mark.parametrize("state, expected_output", test_state_data)
def test_portfolio_agent_should_continue(state, expected_output):
  """portfolio_agent_should_continue unit test"""
  result = portfolio_agent_should_continue(state)
  assert expected_output == result
