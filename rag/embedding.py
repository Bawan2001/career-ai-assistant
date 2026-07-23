from langchain_community.embeddings import HuggingFaceEmbeddings

class EmbeddingEngine:
    """
    Sentence Transformers Embedding Generator.
    Uses 'all-MiniLM-L6-v2' model as specified in technology stack.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name

    def get_embeddings(self):
        """Returns HuggingFaceEmbeddings instance."""
        try:
            return HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        except Exception as e:
            print(f"Error loading HuggingFaceEmbeddings: {e}")
            raise e
