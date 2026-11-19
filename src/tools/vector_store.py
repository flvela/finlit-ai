"""VectorStore class definition"""
from chromadb import PersistentClient

from langchain.embeddings import Embeddings
from langchain_chroma import Chroma

PERSIST_DIRECTORY = 'data/chroma_store'


class VectorStore(Chroma):
  """Implements a Vector store using chromadb Persistent client and langchain_chroma integration.
  Exposes chromadb PersistentClient close() function to avoid zombie connections
  and read-only exceptions after deleting the collection
  """
  client: PersistentClient

  def __init__(self, persist_directory: str, collection_name: str, embedding_function: Embeddings):
    self.client = PersistentClient(path=persist_directory)
    super().__init__(client=self.client, collection_name=collection_name, embedding_function=embedding_function)

  def add_documents_if_empty(self, documents: list) -> Chroma:
    """
    adds documents if existing collection is empty

    Args:
        documents (list): List of documents to be added to the collection
    """
    if super()._collection.count() == 0:
      # load the documents
      super().add_documents(documents)

  def close(self):
    """closes the client connection to the collection
    and releasing the lock on the files"""
    self.client.close()
