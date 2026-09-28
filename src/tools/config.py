"""Configures the Embeddings and LLM based on environment config"""
from dataclasses import dataclass
import os

from dotenv import load_dotenv
from langchain.chat_models import BaseChatModel, init_chat_model
from langchain.embeddings.base import init_embeddings
from langchain_core.embeddings import Embeddings
from chromadb.utils.embedding_functions import HuggingFaceEmbeddingFunction, OpenAIEmbeddingFunction


load_dotenv()  # Load environment variables from .env file

HUGGING_FACE_CONFIG = "huggingface"
OPEN_AI_CONFIG = "openai"

MODEL_PROVIDER = "MODEL_PROVIDER"
MODEL = "MODEL"
MODEL_API_KEY = "MODEL_API_KEY"
EMBEDDINGS_MODEL_PROVIDER = "EMBEDDINGS_MODEL_PROVIDER"
EMBEDDINGS_MODEL = "EMBEDDINGS_MODEL"
EMBEDDINGS_MODEL_API_KEY = "EMBEDDINGS_MODEL_API_KEY"
CHROMA_HUGGINGFACE_API_KEY = "CHROMA_HUGGINGFACE_API_KEY"


@dataclass
class Config:
  """represent config for the application"""
  model_provider: str = os.getenv(MODEL_PROVIDER)
  model_name: str = os.getenv(MODEL)
  model_api_key: str = os.getenv(MODEL_API_KEY)
  embeddings_model_provider: str = os.getenv(EMBEDDINGS_MODEL_PROVIDER)
  embeddings_model_name: str = os.getenv(EMBEDDINGS_MODEL)
  embeddings_model_api_key: str = os.getenv(EMBEDDINGS_MODEL_API_KEY)
  embeddings_by_provider = {
    HUGGING_FACE_CONFIG: HuggingFaceEmbeddingFunction,
    OPEN_AI_CONFIG: OpenAIEmbeddingFunction
  }
  embeddings_kw_args = {}

  def __post_init__(self):
    """Gets the kwargs for init_embeddings based on provider and api key"""
    self.embeddings_kw_args = {
      HUGGING_FACE_CONFIG: {"model_kwargs": {"token": self.embeddings_model_api_key}},
      OPEN_AI_CONFIG: {"openai_api_key": self.embeddings_model_api_key}
    }
    if self.embeddings_model_provider == HUGGING_FACE_CONFIG:
      os.environ[CHROMA_HUGGINGFACE_API_KEY] = self.embeddings_model_api_key

  def get_langchain_embeddings(self) -> Embeddings:
    """
    Get the langchain embeddings model from arguments or environment variables.

    Returns:
      Embeddings: The langchain embeddings model
    """
    if self.embeddings_model_provider in self.embeddings_by_provider:
      return init_embeddings(provider=self.embeddings_model_provider,
                             model=self.embeddings_model_name,
                             **self.embeddings_kw_args[self.embeddings_model_provider])
    raise NotImplementedError(
      (f"Embedddings model provider {self.embeddings_model_provider} is not one of the"
        f" supported providers: {self.embeddings_by_provider.keys()}"))

  def get_chromadb_embeddings(self) -> Embeddings:
    """
    Get the chromadb embeddings model from arguments or environment variables.

    Returns:
      Embeddings: The embeddings model based on environment variables
    """
    if self.embeddings_model_provider in self.embeddings_by_provider:
      return self.embeddings_by_provider[self.embeddings_model_provider](
        api_key_env_var=EMBEDDINGS_MODEL_API_KEY,
        model_name=self.embeddings_model_name)

    raise NotImplementedError(
      (f"Embedddings model provider {self.embeddings_model_provider} is not one of the"
       f" supported providers: {self.embeddings_by_provider.keys()}"))

  def get_llm(self) -> BaseChatModel:
    """
    GET the llm chat model from arguments or environment variables.
    Args:
      model: the name of the model to use
      model_provider: the name of the model provider. Must be supported by langchain init_chat_model parameters
      api_key: the model provider api key.
    """
    return init_chat_model(model=self.model_name,
                           model_provider=self.model_provider,
                           api_key=self.model_api_key)
