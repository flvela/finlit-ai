"""UI config class definition"""
from dataclasses import dataclass

import streamlit as st
from assistant import FinLitAssistant
from frontend.utils.common import (
  CONFIG_ERROR_MESSAGE,
  CONFIG_FAILED,
  EMBEDDINGS_MODEL_API_KEY_CONFIG,
  EMBEDDINGS_MODEL_CONFIG,
  EMBEDDINGS_MODEL_PROVIDER_CONFIG,
  FINANCE_ARTICLE_FILES,
  FINANCE_ARTICLE_FILES_CONFIG,
  MODEL_API_KEY_CONFIG,
  MODEL_CONFIG,
  MODEL_PROVIDER_CONFIG,
  FINLIT_ASSISTANT_CONFIG,
  FINANCE_ARTICLES_CONFIG,
  config_missing_message,
  is_config_complete
)
from tools.config import Config
from tools.articles import load_article_documents

# model provider UI options for selectbox
MODEL_PROVIDER_LABELS = ["OpenAI", "Anthropic"]
# convert from selectbox label to langchain provider
MODEL_PROVIDER_LABEL_TO_CONFIG = {"OpenAI": "openai", "Anthropic": "anthropic"}
# convert from env config or langchain provider to model_provider_options UI label index
MODEL_PROVIDER_CONFIG_TO_LABEL_INDEX = {"openai": 0, "anthropic": 1}
# model options based on provider
MODEL_OPTIONS_BY_PROVIDER = {
  "Anthropic": ["claude-haiku-4-5-20251001", "claude-sonnet-5", "claude-opus-5"],
  "OpenAI": ["gpt-4.0-mini"],
}
# convert from env config or langchain model to model_provider_model_default UI label index
MODEL_CONFIG_TO_LABEL_INDEX = {
  "anthropic": {
    "claude-haiku-4-5-20251001": 0,
    "claude-sonnet-5": 1,
    "claude-opus-5": 2
  },
  "openai": {
    "gpt-4.0-mini": 0
  }
}
EMBEDDINGS_MODEL_PROVIDER_LABELS = ["Hugging Face", "OpenAI"]
# convert from selectbox label to langchain provider
EMEDDINGS_MODEL_PROVIDER_LABEL_TO_CONFIG = {"Hugging Face": "huggingface", "OpenAI": "openai"}
# convert from env config or langchain provider to model_provider_options UI label index
EMBEDDINGS_MODEL_PROVIDER_CONFIG_TO_LABEL_INDEX = {"huggingface": 0, "openai": 1}
EMBEDDINGS_MODEL_OPTIONS_BY_PROVIDER = {
  "Hugging Face": ["google/embeddinggemma-300m"],
  "OpenAI": ["openai/text-embedding-3-small"]
}
EMBEDDINGS_MODEL_CONFIG_TO_LABEL_INDEX = {
  "huggingface": {
    "google/embeddinggemma-300m": 0,
  },
  "openai": {
    "openai/text-embedding-3-small": 0
  }
}


@dataclass
class UIConfig:
  """represents options for the UI application config"""
  env_app_config: Config
  model_provider: str = None
  model: str = None
  model_api_key: str = None
  embeddedings_model_provider: str = None

  def __init__(self):
    self.env_app_config = Config()

  def default_model_provider_index(self):
    """gets the model provider index for model_provider_options based on the given string"""
    model_provider = self.env_app_config.model_provider
    if model_provider is not None and model_provider in MODEL_PROVIDER_CONFIG_TO_LABEL_INDEX:
      return MODEL_PROVIDER_CONFIG_TO_LABEL_INDEX[model_provider]
    return None

  def default_model_index(self):
    """get the model index for  model_provider_model_options based on the given env config model provider and name"""
    if self.model_provider is None:
      config_model_provider = self.env_app_config.model_provider
      config_model_name = self.env_app_config.model_name

      if config_model_provider is not None and config_model_provider in MODEL_CONFIG_TO_LABEL_INDEX:
        return MODEL_CONFIG_TO_LABEL_INDEX[config_model_provider][config_model_name]
    return 0

  def default_embeddings_model_provider_index(self):
    """gets the model provider index for embeddings_model_provider_options based on the given string"""
    config_embeddings_model_provider = self.env_app_config.embeddings_model_provider
    if (config_embeddings_model_provider is not None
        and config_embeddings_model_provider in EMBEDDINGS_MODEL_PROVIDER_CONFIG_TO_LABEL_INDEX):
      return EMBEDDINGS_MODEL_PROVIDER_CONFIG_TO_LABEL_INDEX[config_embeddings_model_provider]
    return None

  def default_embeddings_model_index(self):
    """get the model index for  model_provider_model_options based on the given env config model provider and name"""
    if self.embeddedings_model_provider is not None:
      config_embeddings_model_provider = self.env_app_config.embeddings_model_provider
      config_embeddings_model_name = self.env_app_config.embeddings_model_name
      if (config_embeddings_model_provider is not None
          and config_embeddings_model_provider in EMBEDDINGS_MODEL_CONFIG_TO_LABEL_INDEX):
        return EMBEDDINGS_MODEL_CONFIG_TO_LABEL_INDEX[config_embeddings_model_provider][config_embeddings_model_name]
    return None

  def show_config_sidebar(self):
    """displays the sidebar in the UI"""
    st.session_state[FINANCE_ARTICLE_FILES_CONFIG] = FINANCE_ARTICLE_FILES
    with st.sidebar:
      self.model_provider = st.selectbox(
        "Model Provider", MODEL_PROVIDER_LABELS,
        help="Enter An AI API Model provider. (ie. anthropic, open_ai, etc). The default is in .env file.",
        persist_state="session", key=MODEL_PROVIDER_CONFIG, index=self.default_model_provider_index(),
        on_change=clear_model_api_key)
      model_provider_not_selected = self.model_provider is None
      self.model = st.selectbox(
        "Model", MODEL_OPTIONS_BY_PROVIDER[self.model_provider],
        help="Enter the model to used based on Model Provider. The default is in .env file.",
        persist_state="session", key=MODEL_CONFIG,
        index=self.default_model_index(),
        disabled=model_provider_not_selected,
        on_change=configure_application)
      self.model_api_key = st.text_input(
        "Model API key", type="password",
        help="Enter the Model API key to use for your model. The default is in .env file.",
        persist_state="session", key=MODEL_API_KEY_CONFIG, value=self.env_app_config.model_api_key,
        disabled=model_provider_not_selected,
        on_change=configure_application)
      self.embeddedings_model_provider = st.selectbox(
        "Embeddings Model Provider",  EMBEDDINGS_MODEL_PROVIDER_LABELS,
        help="Enter An Embeddings API Model provider. (ie. anthropic, open_ai, etc). The default is in .env file",
        persist_state="session", key=EMBEDDINGS_MODEL_PROVIDER_CONFIG,
        index=self.default_embeddings_model_provider_index(),
        disabled=model_provider_not_selected,
        on_change=clear_embeddings_model_api_key)
      embeddings_provider_not_selected = model_provider_not_selected and self.embeddedings_model_provider is None
      st.selectbox(
        "Embeddings Model", EMBEDDINGS_MODEL_OPTIONS_BY_PROVIDER[self.embeddedings_model_provider],
        help="Enter the embeddings model to used based on Model Provider. The default is in .env file",
        persist_state="session", key=EMBEDDINGS_MODEL_CONFIG,
        index=self.default_embeddings_model_index(),
        disabled=embeddings_provider_not_selected,
        on_change=configure_application)
      st.text_input(
        "Embeddings Model API key", type="password",
        help="Enter the Embeddings Model API key to use for your model. The default is in .env file",
        persist_state="session", key=EMBEDDINGS_MODEL_API_KEY_CONFIG,
        value=self.env_app_config.embeddings_model_api_key,
        disabled=embeddings_provider_not_selected,
        on_change=configure_application)

      st.button("Configure Application", on_click=configure_application)
      if CONFIG_ERROR_MESSAGE in st.session_state:
        st.error(st.session_state[CONFIG_ERROR_MESSAGE])
      if CONFIG_FAILED in st.session_state and st.session_state[CONFIG_FAILED]:
        st.warning(config_missing_message())

      if is_config_complete():
        configure_application()


def clear_model_api_key():
  """reset the model api key"""
  st.session_state[MODEL_API_KEY_CONFIG] = ""


def clear_embeddings_model_api_key():
  """reset the embeddings model api key"""
  st.session_state[EMBEDDINGS_MODEL_API_KEY_CONFIG] = ""


def configure_application():
  """reset the application configuration"""
  st.session_state.pop(CONFIG_ERROR_MESSAGE, None)
  try:
    finance_articles = []
    st.session_state[FINANCE_ARTICLE_FILES_CONFIG] = FINANCE_ARTICLE_FILES
    for file in FINANCE_ARTICLE_FILES:
      finance_articles.extend(load_article_documents(file))

    st.session_state[FINANCE_ARTICLES_CONFIG] = finance_articles
  except KeyError as e:
    st.session_state[CONFIG_ERROR_MESSAGE] = f"Failed to load finance articles '{FINANCE_ARTICLE_FILES}'. KeyError: {str(e)}"
    st.session_state[CONFIG_FAILED] = True

  if is_config_complete():
    st.session_state[CONFIG_FAILED] = False
    with st.status("Initializing Assistant") as status:
      initialize_assisstant()
      status.update(label="Assistant Initialized", state="complete")
  else:
    st.session_state[CONFIG_FAILED] = True


def initialize_assisstant():
  """initializes the AI Assistant"""
  articles = st.session_state[FINANCE_ARTICLES_CONFIG]
  st.info(st.session_state)
  app_config = Config(
    model_provider=MODEL_PROVIDER_LABEL_TO_CONFIG[st.session_state[MODEL_PROVIDER_CONFIG]],
    model_name=st.session_state[MODEL_CONFIG],
    model_api_key=st.session_state[MODEL_API_KEY_CONFIG],
    embeddings_model_provider=EMEDDINGS_MODEL_PROVIDER_LABEL_TO_CONFIG[st.session_state[EMBEDDINGS_MODEL_PROVIDER_CONFIG]],
    embeddings_model_name=st.session_state[EMBEDDINGS_MODEL_CONFIG],
    embeddings_model_api_key=st.session_state[EMBEDDINGS_MODEL_API_KEY_CONFIG])

  st.session_state[FINLIT_ASSISTANT_CONFIG] = FinLitAssistant(financial_articles=articles, config=app_config)
