import os
from typing import List
from langchain_core.documents import Document

class SimpleTextSplitter:
    """
    Pure Python recursive text splitter matching chunk size and overlap specs.
    Avoids third-party spacy/pydantic compatibility issues on Python 3.14.
    """
    def __init__(self, chunk_size: int = 2500, chunk_overlap: int = 400):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            if end < text_len:
                # Find clean break
                last_newline = text.rfind("\n", start + self.chunk_size // 2, end)
                if last_newline != -1:
                    end = last_newline

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap if end < text_len else text_len
            if start <= 0:
                start = end

        return chunks

class CorpusDocumentLoader:
    """
    Document loader and chunker for domain corpus.
    Configured with assignment specification:
    Chunk size: ~500-800 tokens (~2500 characters)
    Overlap: ~100 tokens (~400 characters)
    """

    def __init__(self, corpus_dir: str = "rag/corpus", chunk_size: int = 2500, chunk_overlap: int = 400):
        self.corpus_dir = corpus_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = SimpleTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def load_and_split(self) -> List[Document]:
        """Load all markdown documents from corpus directory and split into token-aware chunks."""
        if not os.path.exists(self.corpus_dir):
            print(f"Warning: Corpus directory '{self.corpus_dir}' does not exist.")
            return []

        document_chunks = []
        for filename in sorted(os.listdir(self.corpus_dir)):
            if filename.endswith(".md") or filename.endswith(".txt"):
                filepath = os.path.join(self.corpus_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        text_chunks = self.splitter.split_text(content)
                        for chunk in text_chunks:
                            document_chunks.append(Document(
                                page_content=chunk,
                                metadata={"source": filepath, "filename": filename}
                            ))
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

        print(f"Loaded {len(os.listdir(self.corpus_dir))} corpus documents, split into {len(document_chunks)} chunks.")
        return document_chunks
