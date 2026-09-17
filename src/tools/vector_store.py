"""VectorStore class definition"""
from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection

from langchain_chroma import Chroma
from tools.config import Config

PERSIST_DIRECTORY = 'data/chroma_store'


class VectorStore:
  """Implements a Vector store using chromadb Persistent client and langchain_chroma integration.
  Exposes chromadb PersistentClient close() function to avoid zombie connections
  and read-only exceptions after deleting the collection
  """
  client: PersistentClient
  vector_store: Chroma
  persist_directory: str
  collection: Collection
  collection_name: str

  def __init__(self, persist_directory: str, collection_name: str):
    self.client = PersistentClient(path=persist_directory)
    self.persist_directory = persist_directory
    self.collection_name = collection_name

  def get_create_collection(self, documents: list, config: Config = Config()) -> Chroma:
    """
    get or create a vector store collection from the provided documents.
    if collection exists and has documents (count > 0) then the given documents
    are not loaded.

    embedding functions for chromadb and langchain must use the same embeddings algorithm

    Args:
        documents (list): List of documents to be added to the collection
        provider: embeddings model provider
        model: embeddings model name
        api_key: embeddings model provider api key

    Returns:
        Chroma: a langchain Chroma collection
    """
    self.collection = self.client.get_or_create_collection(
       self.collection_name,
       embedding_function=config.get_chromadb_embeddings())
    self.vector_store = Chroma(
        client=self.client,
        collection_name=self.collection_name,
        embedding_function=config.get_langchain_embeddings())
    if self.collection.count() == 0:
      # load the documents
      self.vector_store.add_documents(documents)

    return self.vector_store

  def delete_collection(self):
    """deletes the existing collection"""
    self.vector_store.delete_collection()

  def close(self):
    """closes the client connection to the collection
    and releasing the lock on the files"""
    self.client.close()
