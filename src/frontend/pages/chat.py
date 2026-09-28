"""application page for streamlit app"""
import asyncio

import streamlit as st
from frontend.utils.common import (
  CONFIG_ERROR_MESSAGE,
  FINLIT_ASSISTANT_CONFIG,
  GRAPH_ACTIVITY_CONFIG,
  config_missing_message,
  is_config_complete
)
from frontend.components.fin_lit_container import FinLitActivityContainer
from frontend.components.ui_config import configure_application

# chat roles
ASSISTANT_ROLE = "assistant"
USER_ROLE = "user"


def write_and_save_message(message: str, role: str, message_container):
  """stream the response from AI and adds the message to session state"""
  with message_container:
    with st.chat_message(role):
      st.markdown(message)
    st.session_state.messages.append({"role": role, "content": message})


async def graph_stream_events(prompt: str):
  """Streams graph event status to the UI"""
  assistant = st.session_state[FINLIT_ASSISTANT_CONFIG]
  graph_activity = st.session_state[GRAPH_ACTIVITY_CONFIG]

  stream = await assistant.async_ask(prompt)

  async for item in stream:
    graph_activity.update(item)


def async_chat_with_user(message_container):
  """asynchronous chat with user.
  Args:
    messsage_container: the message container for chat history
    events_container: UI container to publish events
    state_container: UI container to publish state
  """
  assistant = st.session_state[FINLIT_ASSISTANT_CONFIG]
  graph_node_activity = st.session_state[GRAPH_ACTIVITY_CONFIG]

  if "messages" not in st.session_state:
    st.session_state.messages = []
  # display chat history
  with message_container:
    for message in st.session_state.messages:
      with st.chat_message(message["role"]):
        st.markdown(message["content"])

  # get new user input
  if prompt := st.chat_input("Say something"):
    write_and_save_message(prompt, USER_ROLE, message_container)

    if prompt == "/clear_chat":
      st.session_state.messages = []
      assistant.reset()
    else:
      if assistant.get_interrupt_value() is None:
        # start a new chat thread if assistant is not interrupted
        assistant.reset()
        graph_node_activity.reset_node_statuses()
      # stream events from assistant
      with message_container.status(label="Processing", state="running"):
        asyncio.run(graph_stream_events(prompt))
      result = assistant.get_last_message()
      write_and_save_message(result, ASSISTANT_ROLE, message_container)


def async_ai_assistant_page():
  """defines the streamlit AI Assistant chat page"""
  st.set_page_config(layout="wide")

  st.header("Snack Stack AI Assistant", text_alignment="center")

  if is_config_complete():
    if FINLIT_ASSISTANT_CONFIG not in st.session_state:
      configure_application()

    col1, col2 = st.columns([2, 1])
    col1.subheader("Conversation")
    col2.subheader("Graph Activity")
    col2.badge(label="Graph activity populated after first query", color="blue", icon=":material/info:")

    graph_tab, state_tab, events_tab = col2.tabs(["Graph", "State", "Events"])

    if GRAPH_ACTIVITY_CONFIG not in st.session_state:
      st.session_state[GRAPH_ACTIVITY_CONFIG] = FinLitActivityContainer()

    st.session_state[GRAPH_ACTIVITY_CONFIG].initialize_state_container(state_tab)
    st.session_state[GRAPH_ACTIVITY_CONFIG].initialize_events_container(events_tab)

    with col2:
      graph_container = graph_tab.container(key="graph_container", border=False, gap="xxsmall", width="content")
      st.session_state[GRAPH_ACTIVITY_CONFIG].initialize_nodes_container(graph_container)
    with col1:
      message_container = st.container(key="message_container", border=False, height=500, gap="xxsmall")
      async_chat_with_user(message_container)
  else:
    if CONFIG_ERROR_MESSAGE in st.session_state:
      st.error(st.session_state[CONFIG_ERROR_MESSAGE])
    st.warning(f"Please configure your application in sidebar. {config_missing_message()}")


async_ai_assistant_page()
