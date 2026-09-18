"""tests for router node"""
import pytest

from agents.router import route_decision, router_node
from agents.state import (
  FINANCE_FAQ,
  MESSAGES_FIELD,
  PORTFOLIO_ANALYSIS,
  ROUTE_FIELD,
  ROUTE_STATES,
  USER_INPUT_FIELD,
  FinLitState
)
from testutils.common import init_test_runtime

test_data = [
  ("what is the difference between RSU and ESPP", FINANCE_FAQ),
  ("I would like to analyze my stock portofolio", PORTFOLIO_ANALYSIS)
]


@pytest.mark.parametrize("user_input, expected_output", test_data)
def test_router_node(user_input: str, expected_output: str):
  """tests the router node"""
  state = FinLitState()
  state[USER_INPUT_FIELD] = user_input
  result = router_node(state, init_test_runtime())
  assert result[ROUTE_FIELD] == expected_output
  assert len(result[MESSAGES_FIELD]) == 1
  assert result[MESSAGES_FIELD][0].content == user_input


def test_route_decision():
  """tests the route_decision function"""
  state = FinLitState()
  for route in ROUTE_STATES:
    state[ROUTE_FIELD] = route
    assert route_decision(state) == route
