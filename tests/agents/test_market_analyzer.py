"""Unit tests for Portfolio Analyzer Agent"""
import pytest

from langchain.messages import AIMessage, ToolCall

from agents.market_analyzer import market_analysis_agent_node, market_analysis_agent_should_continue
from agents.state import (
  MARKET_ANALYSIS_TOOLS,
  GRAPH_END,
  MESSAGES_FIELD,
  USER_INPUT_FIELD,
  FinLitState
)
from testutils.common import assert_agent_node_output_state, init_test_runtime
from tools.logger import get_logger

logger = get_logger(__name__)

test_data = [
  # user input and true/false if we should call tools
  ("how are markets moving today", True),
  ("what are the latest news for IBM", True),
  ("What are the top companies in healthcare sector", True)
]


@pytest.mark.parametrize("user_input, has_tool_calls", test_data)
def test_market_analysis_agent_node(user_input: str, has_tool_calls: bool):
  """unit test for market_analysis_agent_node"""
  state = FinLitState()
  state[USER_INPUT_FIELD] = user_input
  result = market_analysis_agent_node(state, init_test_runtime())
  assert_agent_node_output_state(result, has_tool_calls)


tool_call = ToolCall({"name": "foo", "args": {"a": 1}, "id": "123"})

test_state_data = [
  ({}, GRAPH_END),
  ({MESSAGES_FIELD: [AIMessage(content="", tool_calls=[tool_call])]}, MARKET_ANALYSIS_TOOLS),
  ({MESSAGES_FIELD: []}, GRAPH_END),
  ({MESSAGES_FIELD: [{"content", "any_content"}]}, GRAPH_END)
]


@pytest.mark.parametrize("state, expected_output", test_state_data)
def test_market_analysis_agent_should_continue(state, expected_output):
  """market_analysis_agent_should_continue unit test"""
  result = market_analysis_agent_should_continue(state)
  assert expected_output == result
