import os
import chromadb
import ollama
from typing import List, Dict

class VectorMemoryManager:
    """Manages persistent semantic memory using ChromaDB and Ollama local embeddings."""
    def __init__(self, db_path: str = None, embed_model: str = "nomic-embed-text"):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                "vector_db"
            )
        self.db_path = db_path
        self.embed_model = embed_model
        
        # Initialize standard memory backup as well
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(name="conversations")
        
        # Used to assign unique IDs to vector chunks
        self._doc_counter = self.collection.count()

    def _get_embedding(self, text: str) -> List[float]:
        """Generates an embedding vector using Ollama."""
        try:
            response = ollama.embeddings(model=self.embed_model, prompt=text)
            return response['embedding']
        except Exception as e:
            print(f"Embedding generation failed. Make sure you have pulled '{self.embed_model}'. Error: {e}")
            # Fallback to zeros (not ideal, but prevents crash if model missing initially)
            return [0.0] * 768

    def add_interaction(self, user_id: str, role: str, content: str):
        """Indexes a new interaction into the vector database."""
        # Simple JSON-like metadata
        document = f"Role: {role}\nContent: {content}"
        metadata = {"user_id": str(user_id), "role": role}
        
        try:
            embedding = self._get_embedding(document)
            
            self.collection.add(
                embeddings=[embedding],
                documents=[document],
                metadatas=[metadata],
                ids=[f"doc_{self._doc_counter}"]
            )
            self._doc_counter += 1
        except Exception as e:
            print(f"Failed to save to vector memory: {e}")

    def semantic_search(self, user_id: str, query: str, n_results: int = 5) -> str:
        """Searches past semantic context regarding the current query."""
        if self.collection.count() == 0:
            return "No previous semantic memory exists."
            
        try:
            query_embedding = self._get_embedding(query)
            
            # Retrieve from ChromaDB filtered by user
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, self.collection.count()),
                where={"user_id": str(user_id)}
            )
            
            documents = results.get('documents', [[]])[0]
            
            if not documents:
                return "No relevant past memories found regarding this."
                
            context = "--- RELEVANT PAST SEMANTIC MEMORY ---\n"
            for doc in documents:
                context += doc + "\n\n"
            return context.strip() + "\n-------------------------------------\n"
            
        except Exception as e:
            print(f"Vector search failed: {e}")
            return "Error retrieving semantic memory."
