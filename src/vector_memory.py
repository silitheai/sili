import os
import chromadb
import ollama
from typing import List, Dict

class VectorMemoryManager:
    """Manages persistent semantic memory using ChromaDB and Ollama local embeddings."""
    def __init__(self, db_path: str = None, embed_model: str = "nomic-embed-text", host: str = "http://localhost:11434"):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                "vector_db"
            )
        self.db_path = db_path
        self.embed_model = embed_model
        self.client_ollama = ollama.AsyncClient(host=host)
        
        # Initialize standard memory backup as well
        self.client_chroma = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client_chroma.get_or_create_collection(name="conversations")
        
        # Used to assign unique IDs to vector chunks
        self._doc_counter = self.collection.count()

    async def _get_embedding(self, text: str) -> List[float]:
        """Generates an embedding vector using Ollama (Async)."""
        try:
            response = await self.client_ollama.embeddings(model=self.embed_model, prompt=text)
            return response['embedding']
        except Exception as e:
            if "not found" in str(e).lower():
                print(f"CRITICAL: Embedding model '{self.embed_model}' not found. Please run 'ollama pull {self.embed_model}' in your terminal.")
            else:
                print(f"Embedding generation failed: {e}")
            # Fallback to zeros to prevent complete failure of the agent
            return [0.0] * 768

    async def add_interaction(self, user_id: str, role: str, content: str, topic: str = "General"):
        """Indexes a new interaction with Thematic Metadata and Recency tagging."""
        import time
        document = f"Role: {role}\nContent: {content}"
        metadata = {
            "user_id": str(user_id), 
            "role": role, 
            "topic": topic, 
            "timestamp": time.time()
        }
        
        try:
            embedding = await self._get_embedding(document)
            self.collection.add(
                embeddings=[embedding],
                documents=[document],
                metadatas=[metadata],
                ids=[f"doc_{self._doc_counter}"]
            )
            self._doc_counter += 1
        except Exception as e:
            print(f"Failed to save to vector memory: {e}")

    def thematic_search(self, user_id: str, topic: str, n_results: int = 5) -> str:
        """Retrieves memories filtered by a specific neural theme."""
        if self.collection.count() == 0:
            return f"No memories found for topic: {topic}"
            
        try:
            results = self.collection.query(
                query_texts=[topic], # Text-based search on the topic theme
                n_results=min(n_results, self.collection.count()),
                where={"$and": [{"user_id": str(user_id)}, {"topic": topic}]}
            )
            
            documents = results.get('documents', [[]])[0]
            if not documents:
                return f"No relevant past memories found for theme: {topic}."
                
            context = f"--- RELATED PAST {topic.upper()} MEMORY ---\n"
            for doc in documents:
                context += doc + "\n\n"
            return context.strip() + "\n-------------------------------------\n"
        except Exception as e:
            print(f"Thematic search failed: {e}")
            return "Error retrieving thematic memory."

    async def semantic_search(self, user_id: str, query: str, n_results: int = 5) -> str:
        """Searches past semantic context with recency-weighted preference (simulated)."""
        if self.collection.count() == 0:
            return "No previous semantic memory exists."
            
        try:
            query_embedding = await self._get_embedding(query)
            # Use query with Chroma (Chroma performs the search)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, self.collection.count()),
                where={"user_id": str(user_id)}
            )
            
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            if not documents:
                return "No relevant past memories found regarding this."
            
            # Simulated Recency Ranking: Sort results by timestamp if available
            combined = sorted(zip(documents, metadatas), key=lambda x: x[1].get('timestamp', 0), reverse=True)
                
            context = "--- RELEVANT PAST SEMANTIC MEMORY ---\n"
            for doc, meta in combined:
                context += f"[{meta.get('topic', 'General')}] " + doc + "\n\n"
            return context.strip() + "\n-------------------------------------\n"
        except Exception as e:
            print(f"Vector search failed: {e}")
            return "Error retrieving semantic memory."
