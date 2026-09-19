"""Defines Graph activity classes and related functions for display graph status in UI"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
import time
from typing import Any

from langgraph.errors import GraphInterrupt

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from frontend.utils.common import format_time

# graph stream event types
EVENT_ON_CHAIN_START = 'on_chain_start'
EVENT_ON_CHAIN_END = "on_chain_end"
EVENT_ON_TOOL_START = "on_tool_start"
EVENT_ON_TOOL_END = "on_tool_end"
EVENT_ON_TOOL_ERROR = "on_tool_error"
EVENT_ON_CHAT_MODEL_START = "on_chat_model_start"
EVENT_ON_CHAT_MODEL_END = "on_chat_model_end"
EVENT_ON_PARSER_START = "on_parser_start"
EVENT_ON_PARSER_END = "on_parser_end"

# full graph node
LANGRAPH_NODE_NAME = "LangGraph"

# status texts
STATUS_NOT_STARTED = ":grey-badge[:material/hourglass_top: Not Started]"
STATUS_RUNNING = ":yellow-badge[:material/cached: Running]"
STATUS_PAUSED = ":orange-badge[:material/pause: Paused]"
STATUS_COMPLETED = ":green-badge[:material/check_small: Completed]"

# graph stream event keys
DATA_KEY = 'data'
ERROR_KEY = 'error'
EVENT_KEY = 'event'
INPUT_KEY = 'input'
LANGGRAPH_NODE_KEY = 'langgraph_node'
METADATA_KEY = "metadata"
NAME_KEY = 'name'
OUTPUT_KEY = 'output'
THREAD_ID_KEY = 'thread_id'

# Langgraph event key states
STATE_COMPLETE_EVENT_KEYS = [EVENT_ON_CHAIN_END, EVENT_ON_CHAT_MODEL_END, EVENT_ON_TOOL_END, EVENT_ON_PARSER_END]
STATE_PAUSED_EVENT_KEYS = [EVENT_ON_TOOL_ERROR]
STATE_START_EVENT_KEYS = [EVENT_ON_CHAIN_START, EVENT_ON_CHAT_MODEL_START, EVENT_ON_TOOL_START, EVENT_ON_PARSER_START]
TOOL_EVENTS = [EVENT_ON_TOOL_START, EVENT_ON_TOOL_END, EVENT_ON_TOOL_ERROR]


@dataclass
class GraphNode:
  """used to keep track and display of graph node status """
  # name of the graph node as it it appear in langgraph
  name: str
  # UI status placeholder to write node status updates
  status_placeholder: DeltaGenerator
  # start time for the current run
  start_time: float
  # UI time placeholder to write node status execution time
  time_placeholder: DeltaGenerator
  # total run time for node across multiple runs
  total_run_time: float
  # the status text to display in UI
  status_text: str

  def update_status(self, state: str, update_time):
    """updates the status of the node"""
    if self.status_placeholder:
      self.status_placeholder.markdown(state, text_alignment="right")
    self.status_text = state

    if state == STATUS_RUNNING:
      self.start_time = update_time
    elif state == STATUS_COMPLETED:
      elapsed_time_ms = (update_time - self.start_time) * 1000
      self.total_run_time = self.total_run_time + elapsed_time_ms
      if self.time_placeholder:
        self.time_placeholder.markdown(f"{format_time(self.total_run_time)}", text_alignment="right")


def build_graph_state_placeholder(label: str, state_parent: DeltaGenerator) -> DeltaGenerator:
  """builds a graph state placeholder in the state parent container with the given label"""
  label_container = state_parent.container(border=True, gap="xxsmall")
  label_col, data_col = label_container.columns([1, 3])
  label_col.write(label)
  placeholder = data_col.empty()
  placeholder.markdown("--", text_alignment="left")
  return placeholder


@dataclass
class GraphStateContainer:
  """Keep track of UI placeholders to display graph state"""
  # field name to placeholder mapping. The label should match graph state field found in LangGraph event
  field_name_to_placeholder: dict[str, DeltaGenerator]

  def __init__(self, state_container: DeltaGenerator, field_name_to_placeholder: dict[str, DeltaGenerator]):
    """creates all the containers and placeholders in the state parent container for UI to display graph state"""
    self.field_name_to_placeholder = field_name_to_placeholder
    self.field_name_to_placeholder[THREAD_ID_KEY] = build_graph_state_placeholder(THREAD_ID_KEY, state_container)

  def update_graph_state(self, langgraph_event_item):
    """updates the graph status UI based on the langraph event"""
    self.field_name_to_placeholder[THREAD_ID_KEY].markdown(
      langgraph_event_item[METADATA_KEY][THREAD_ID_KEY], text_alignment="left")
    if DATA_KEY in langgraph_event_item:
      event_data = langgraph_event_item[DATA_KEY]
      if INPUT_KEY in event_data:
        input_data = event_data[INPUT_KEY]
        if isinstance(input_data, dict):
          # for LangGraph event node input can be a Command type in case of graph interrupt
          # we want to skip this as
          self.update_graph_state_fields(input_data)
      if OUTPUT_KEY in event_data:
        output_data = event_data[OUTPUT_KEY]
        self.update_graph_state_fields(output_data)

  def update_graph_state_fields(self, event_field_data: dict):
    """updates graph state field placeholders with data found in the LangGraph event"""
    for field_name, placeholder in self.field_name_to_placeholder.items():
      if field_name in event_field_data:
        placeholder.markdown(event_field_data[field_name], text_alignment="left")


@dataclass
class GraphEventNode:
  """class used to track nodes for GraphEventActivity class"""
  # the name of this event node
  name: str
  # Optional parent_event_container, if null this is the parent
  parent_event_container: DeltaGenerator
  # child event containers
  child_event_containers: dict[str, DeltaGenerator]
  # start time by event names
  start_time_by_event_name: dict[str, float]

  def __init__(self, name: str, events_container: DeltaGenerator):
    """creates the GraphEventActivityNode with given name"""
    self.name = name
    self.parent_event_container = events_container.status(self.name, expanded=True)
    self.child_event_containers = {}
    self.start_time_by_event_name = {}

  def create_child_event_container(self, child_name: str):
    """creates a child event event container if needed based on child name"""
    if child_name != self.name and child_name not in self.child_event_containers:
      self.child_event_containers[child_name] = self.parent_event_container.status(child_name, expanded=True)

  def update_start_time(self, node_name: str, event_key: str, start_time: float):
    """set the start time for parent and children based on the node name"""
    if event_key in STATE_START_EVENT_KEYS:
      self.start_time_by_event_name[node_name] = start_time

  def get_start_time(self, node_name: str) -> float:
    """get the start time for parent and children based on the node name"""
    return self.start_time_by_event_name[node_name]

  def update_event_container(self, node_name: str, event_key: str, update_time: float, item: Any):
    """update parent event container"""
    if self.name != node_name:
      # this update is for a child event container
      status_container = self.child_event_containers[node_name]
    else:
      # this update is for this container
      status_container = self.parent_event_container

    total_time = (update_time - self.get_start_time(node_name)) * 1000
    state_complete = event_key in STATE_COMPLETE_EVENT_KEYS
    state_text = "complete" if state_complete else "running"

    with status_container.expander(event_key):
      st.write(item)
    status_container.update(label=self.get_label(node_name, event_key, total_time),
                            state=state_text,
                            expanded=not state_complete)

  def get_label(self, node_name: str,  event_key: str, total_time: float) -> str:
    """get the label_color base on event key"""
    if event_key in STATE_COMPLETE_EVENT_KEYS:
      return f":green[{node_name}\n({format_time(total_time)})]"

    if event_key in STATE_PAUSED_EVENT_KEYS:
      return f":orange[{node_name}\n({format_time(total_time)})]"

    return f":yellow[{node_name}\n({format_time(total_time)})]"


@dataclass
class GraphEventContainer:
  """class used to display events streamed from Langgraph"""
  parent_event_containers: dict[dict, GraphEventNode]
  events_container: DeltaGenerator

  def __init__(self, events_container: DeltaGenerator):
    """Contructor for GraphEventActivity"""
    self.parent_event_containers = {}
    self.events_container = events_container

  def get_parent_name(self, langgraph_item) -> str:
    """returns the parent of the LangGraph event item"""
    if LANGGRAPH_NODE_KEY in langgraph_item[METADATA_KEY]:
      return langgraph_item[METADATA_KEY][LANGGRAPH_NODE_KEY]

    return langgraph_item[NAME_KEY]

  def update_event(self, langgraph_item, update_time):
    """Updates the UI event container based on the given langgraph event item"""
    node_name = langgraph_item[NAME_KEY]
    parent_name = self.get_parent_name(langgraph_item)

    if parent_name not in self.parent_event_containers:
      self.parent_event_containers[parent_name] = GraphEventNode(parent_name, self.events_container)

    parent_node = self.parent_event_containers[parent_name]
    parent_node.create_child_event_container(node_name)

    event_key = langgraph_item[EVENT_KEY]
    parent_node.update_start_time(node_name=node_name, event_key=event_key, start_time=update_time)
    parent_node.update_event_container(node_name=node_name, event_key=event_key, update_time=update_time, item=langgraph_item)
    if (parent_name == node_name and event_key in STATE_COMPLETE_EVENT_KEYS):
      del self.parent_event_containers[parent_name]


@dataclass
class GraphActivityContainer(ABC):
  """parent container used to show Langraph node status, graph state and events in the UI"""
  node_statuses_by_name: dict
  state_container: GraphStateContainer
  events_container: GraphEventContainer

  def __init__(self):
    self.node_statuses_by_name = {}
    self.state_container = None
    self.events_container = None

  def initialize_state_container(self, state_container: DeltaGenerator):
    """initializes the state activity with the UI state container"""
    # create state field containers specific to graph state
    field_name_to_placeholder = self.get_state_field_name_placeholders(state_container)
    self.state_container = GraphStateContainer(state_container, field_name_to_placeholder=field_name_to_placeholder)

  @abstractmethod
  def get_state_field_name_placeholders(self, state_container: DeltaGenerator):
    """initialized the field name to placeholder container to display graph state in UI"""

  def initialize_events_container(self, events_container: DeltaGenerator):
    """initializes the events activity with the UI events container"""
    self.events_container = GraphEventContainer(events_container)

  @abstractmethod
  def initialize_nodes_container(self, graph_container: DeltaGenerator):
    """Builds the UI containers to show graph status in the graph_container.
    it must be implemented by subclass
    """

  def initialize_graph_node(self, node_name: str, parent_container: DeltaGenerator):
    """initializes the graph status and placeholder status container in the parent_container"""
    node_container = parent_container.container(key=node_name, border=True, gap="xxsmall")
    node_col, status_col = node_container.columns(2)
    node_col.write(node_name.replace("_", " ").title())
    status_placeholder = status_col.empty()
    time_placeholder = status_col.empty()
    if node_name in self.node_statuses_by_name:
      graph_node = self.node_statuses_by_name[node_name]
      graph_node.status_placeholder = status_placeholder
      graph_node.time_placeholder = time_placeholder
    else:
      graph_node = GraphNode(
        node_name,
        status_placeholder=status_placeholder,
        start_time=0,
        time_placeholder=time_placeholder,
        total_run_time=0,
        status_text=STATUS_NOT_STARTED)
      self.node_statuses_by_name[node_name] = graph_node

    node_status = graph_node.status_text
    time_text = format_time(graph_node.total_run_time)
    status_placeholder.markdown(node_status, text_alignment="right")
    time_placeholder.markdown(time_text, text_alignment="right")

  def update_node_status(self, langgraph_event_item, update_time):
    """updates the node status in UI based on the node name and langgraph_event_item"""
    node_name = langgraph_event_item[NAME_KEY]
    event_key = langgraph_event_item[EVENT_KEY]
    if event_key in TOOL_EVENTS:
      # if this is a tool event look up parent name as name key is name of tool
      # and not the tool node
      node_name = langgraph_event_item[METADATA_KEY][LANGGRAPH_NODE_KEY]

    if node_name in self.node_statuses_by_name:
      # if node name exists it means it is tracked in graph tab
      node_status = self.node_statuses_by_name[node_name]

      if event_key in STATE_START_EVENT_KEYS:
        node_status.update_status(STATUS_RUNNING, update_time)
      elif event_key in STATE_COMPLETE_EVENT_KEYS:
        node_status.update_status(STATUS_COMPLETED, update_time)
      elif event_key in STATE_PAUSED_EVENT_KEYS:
        error = langgraph_event_item[DATA_KEY][ERROR_KEY]
        if isinstance(error, GraphInterrupt):
          node_status.update_status(STATUS_PAUSED, update_time)

  def update(self, langgraph_event_item):
    """Main method to update Graph activity for Graph, State and Events tab based on LangGraph events"""
    update_time = time.perf_counter()
    if self.state_container is not None:
      self.state_container.update_graph_state(langgraph_event_item)
    self.update_node_status(langgraph_event_item, update_time)
    if self.events_container is not None:
      self.events_container.update_event(langgraph_event_item, update_time)

  def reset_node_statuses(self):
    """reset the graph node status and time placeholders"""
    for _, node in self.node_statuses_by_name.items():
      node.status_text = STATUS_NOT_STARTED
      node.total_run_time = 0
      node.start_time = 0
      if node.status_placeholder:
        node.status_placeholder.markdown(STATUS_NOT_STARTED, text_alignment="right")
      if node.time_placeholder:
        node.time_placeholder.markdown("--", text_alignment="right")
