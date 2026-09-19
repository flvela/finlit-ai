"""FinLit AI Activity container implementation"""
from streamlit.delta_generator import DeltaGenerator

from agents.state import (
  OUTPUT_FIELD,
  USER_INPUT_FIELD
)
from agents.graph import (
  FINANCE_FAQ_NODE,
  FINANCE_FAQ_TOOL_NODE,
  ROUTER_NODE
)
from frontend.components.graph_containers import (
  GraphActivityContainer,
  LANGRAPH_NODE_NAME,
  build_graph_state_placeholder
)


class FinLitActivityContainer(GraphActivityContainer):
  """FinLit AI graph container class used to display graph nodes, state and events in UI"""

  def initialize_nodes_container(self, graph_container: DeltaGenerator):
    """Builds the UI containers to show graph status in the graph_container"""
    self.initialize_graph_node(ROUTER_NODE, graph_container)
    self.initialize_graph_node(FINANCE_FAQ_NODE, graph_container)
    self.initialize_graph_node(FINANCE_FAQ_TOOL_NODE, graph_container)
    self.initialize_graph_node(LANGRAPH_NODE_NAME, graph_container)

  def get_state_field_name_placeholders(self, state_container: DeltaGenerator):
    """initialized the field name to placeholder container to display graph state in UI"""
    return {
      USER_INPUT_FIELD: build_graph_state_placeholder(USER_INPUT_FIELD, state_container),
      OUTPUT_FIELD: build_graph_state_placeholder(OUTPUT_FIELD, state_container),
    }
