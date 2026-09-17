"""Unit Tests for Config"""
import os

from dotenv import load_dotenv

from langchain.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from tools.config import Config

load_dotenv()


def test_get_langchain_embeddings():
  """test get_langchain_embeddings with default params. Ensures project is configured correctly"""
  config = Config()
  embeddings = config.get_langchain_embeddings()
  assert embeddings is not None, "Embeddings should not be None"
  assert isinstance(embeddings, Embeddings)


def test_get_llm():
  """test get_llm with default params. Ensures project is configured correctly"""
  config = Config()
  llm = config.get_llm()
  assert llm is not None, "LLM should not be None"
  assert isinstance(llm, BaseChatModel)


def test_get_chromadb_embeddings():
  """test get_chromadb_embeddings with default params. Ensures project is configured correctly"""
  provider = os.getenv("EMBEDDINGS_MODEL_PROVIDER")
  config = Config()
  embeddings = config.get_chromadb_embeddings()
  assert embeddings is not None, "Embeddings should not be None"
  assert isinstance(embeddings, config.embeddings_by_provider[provider])


def test_config_post_init__():
  """tests the contructor for Config class"""
  config = Config()
  expected_kw_args = {
    "huggingface": {"model_kwargs": {"token": config.embeddings_model_api_key}},
    "openai": {"openai_api_key": config.embeddings_model_api_key}
  }
  assert config.embeddings_kw_args == expected_kw_args
