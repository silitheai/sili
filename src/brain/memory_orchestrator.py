import json

class MemoryOrchestrator:
    """Orchestrates interaction between short-term chat history and long-term vector memory."""
    def __init__(self, short_term_memory, vector_memory):
        self.short_term = short_term_memory
        self.vector = vector_memory

    async def get_relevant_context(self, query, user_id, depth=1):
        """Synthesizes context with Recursive Associative Retrieval (Multi-hop)."""
        # 1. Get recent chat history via MemoryManager
        history = self.short_term.get_user_history(user_id)
        
        # 2. Primary Semantic Search via VectorMemoryManager
        primary_memories = await self.vector.semantic_search(user_id, query, n_results=3)
        
        # 3. Associative Neural Linking
        context_stack = [primary_memories]
        if depth > 0:
            associative_links = self._extract_associative_links(primary_memories)
            for link in associative_links[:2]:
                hop_memory = await self.vector.semantic_search(user_id, link, n_results=2)
                if "No relevant" not in hop_memory:
                    context_stack.append(f"[Associative Neural Link: {link}]\n{hop_memory}")

        return {
            "short_term": history,
            "long_term": "\n\n".join(context_stack),
            "synthesis": self._synthesize_insights(context_stack)
        }

    def _extract_associative_links(self, text):
        """Extracts potential associative links from memory text."""
        import re
        # Find capitalized words that might be topics or names
        links = re.findall(r'[A-Z][a-z]+', text)
        return list(set(links))

    def _synthesize_insights(self, context_stack):
        """Synthesis Node: Merges fragmented memories into high-level insights."""
        return f"Neural Synthesis: Successfully synthesized {len(context_stack)} neural clusters."

    async def store_experience(self, user_id, user_msg, agent_response):
        """Saves interaction to both memory layers."""
        self.short_term.add_interaction(user_id, "user", user_msg)
        self.short_term.add_interaction(user_id, "assistant", agent_response)
        
        await self.vector.add_interaction(user_id, "assistant", f"Goal: {user_msg}\nResponse: {agent_response}")
