"""Defines common constants and functions used for the streamlit app"""
import streamlit as st

# session state config keys
MODEL_CONFIG = "model"
MODEL_PROVIDER_CONFIG = "model_provider"
MODEL_API_KEY_CONFIG = "model_api_key"
EMBEDDINGS_MODEL_PROVIDER_CONFIG = "embeddings_model_provider"
EMBEDDINGS_MODEL_API_KEY_CONFIG = "embeddings_model_api_key"
EMBEDDINGS_MODEL_CONFIG = "embeddings_model"
FINLIT_ASSISTANT_CONFIG = "finlit_assistant"
FINANCE_ARTICLE_FILES_CONFIG = "finance_article_files"
GRAPH_ACTIVITY_CONFIG = "graph_activity_config"
FINANCE_ARTICLES_CONFIG = "finance_articles"
PORTFOLIO_MANAGER_CONFIG = "portfolio_manager"
REQUIRED_CONFIG = [
  MODEL_CONFIG,
  MODEL_PROVIDER_CONFIG,
  MODEL_API_KEY_CONFIG,
  EMBEDDINGS_MODEL_PROVIDER_CONFIG,
  EMBEDDINGS_MODEL_API_KEY_CONFIG,
  EMBEDDINGS_MODEL_CONFIG
]
CONFIG_FAILED = "config_failed"
CONFIG_ERROR_MESSAGE = "config_error_messages"
FINANCE_ARTICLE_FILES = ["data/finance_edu/aicpa_articles.json", "data/finance_edu/investopedia_articles.json"]


def setting_exists(setting_name: str):
  """Helper method to check if setting exists in session state"""
  return (setting_name in st.session_state and st.session_state[setting_name] != ""
          and st.session_state[setting_name] is not None)


def is_config_complete() -> bool:
  """Checks if the user has set all the config required"""
  for setting in REQUIRED_CONFIG:
    if not setting_exists(setting):
      return False
  return True


def config_missing_message() -> str:
  """Gets a list of the missing required config settings"""
  missing_settings = []
  for setting in REQUIRED_CONFIG:
    if not setting_exists(setting):
      missing_settings.append(setting)
  return f"Missing settings are {missing_settings}"


def format_time(time_ms: float) -> str:
  """returns a string of the time + units.
    Ex 1: time_ms = 1000 -> 1 s
    Ex 2: time_ms = 10 -> 10 ms
  """
  if time_ms == 0:
    return "--"
  return f"{time_ms/1000:.2f} s" if time_ms > 900 else f"{time_ms:.2f} ms"
