import os
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from rag.document_loader import CorpusDocumentLoader
from rag.embedding import EmbeddingEngine

class FAISSVectorStoreManager:
    """
    FAISS Vector Database Manager for building, persisting, and querying the RAG knowledge base.
    """

    def __init__(self, index_path: str = "rag/faiss_index"):
        self.index_path = index_path
        self.embedding_engine = EmbeddingEngine()
        self.vector_store: Optional[FAISS] = None

    def initialize_vector_store(self, force_rebuild: bool = False) -> FAISS:
        """Loads existing FAISS index or builds a new one from corpus documents."""
        embeddings = self.embedding_engine.get_embeddings()

        if not force_rebuild and os.path.exists(self.index_path):
            try:
                print(f"Loading existing FAISS vector store from '{self.index_path}'...")
                self.vector_store = FAISS.load_local(
                    self.index_path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                return self.vector_store
            except Exception as e:
                print(f"Failed to load FAISS index: {e}. Rebuilding...")

        # Build index from corpus
        print("Building new FAISS vector database from corpus...")
        loader = CorpusDocumentLoader()
        chunks = loader.load_and_split()

        if not chunks:
            # Emergency dummy chunk if corpus is unreadable
            chunks = [Document(page_content="ATS resume optimization guidelines recommend using standard section headers and clear metrics.", metadata={"source": "default"})]

        self.vector_store = FAISS.from_documents(chunks, embeddings)
        
        os.makedirs(self.index_path, exist_ok=True)
        self.vector_store.save_local(self.index_path)
        print(f"FAISS vector database built and saved to '{self.index_path}'.")
        return self.vector_store

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Perform similarity search against the vector database."""
        if not self.vector_store:
            self.initialize_vector_store()
        return self.vector_store.similarity_search(query, k=k)
