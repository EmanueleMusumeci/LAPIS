
import os
import json
import math
from typing import List, Dict, Any, Optional

class VectorDB:
    def __init__(self, db_path: str, client: Any):
        """
        Initialize the Vector Database.
        
        Args:
            db_path (str): Path to the JSON file where the DB is stored.
            client: OpenAI client (or compatible) for generating embeddings.
        """
        self.db_path = db_path
        self.client = client
        self.data: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        """Load the database from the JSON file."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                self.data = []
                print(f"Warning: Could not decode JSON from {self.db_path}. Starting with empty DB.")
        else:
            self.data = []

    def save(self):
        """Save the database to the JSON file."""
        dirname = os.path.dirname(self.db_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def _get_embedding(self, text: str) -> List[float]:
        """Get the embedding for a given text.

        Uses the OpenAI embeddings API. When the client is an Anthropic client
        (which has no embeddings endpoint), falls back to constructing an OpenAI
        client from the OPENAI_API_KEY environment variable.
        """
        text = text.replace("\n", " ")
        client = self.client

        # Anthropic clients don't support embeddings — fall back to OpenAI.
        client_module = type(client).__module__ or ""
        if "anthropic" in client_module.lower():
            import os
            from openai import OpenAI
            openai_key = os.getenv("OPENAI_API_KEY", "")
            if not openai_key:
                print("Warning: OPENAI_API_KEY not set; cannot generate embeddings.")
                return []
            client = OpenAI(api_key=openai_key)

        try:
            return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []

    def add(self, issue: str, solution: str, metadata: Optional[Dict] = None):
        """
        Add a new entry to the database.
        
        Args:
            issue (str): The issue description.
            solution (str): The proposed solution.
            metadata (Optional[Dict]): Additional metadata.
        """
        if not issue or not solution:
            return

        embedding = self._get_embedding(issue)
        if not embedding:
            return

        entry = {
            "issue": issue,
            "solution": solution,
            "embedding": embedding,
            "metadata": metadata or {}
        }
        self.data.append(entry)
        self.save()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)

    def search(self, query: str, k: int = 1, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar issues in the database.
        
        Args:
            query (str): The query string (new issue).
            k (int): Number of results to return.
            threshold (float): Minimum similarity threshold (0 to 1).
            
        Returns:
            List[Dict]: List of matching entries.
        """
        if not self.data:
            return []

        query_embedding = self._get_embedding(query)
        if not query_embedding:
            return []

        results = []

        for entry in self.data:
            entry_vec = entry['embedding']
            similarity = self._cosine_similarity(query_embedding, entry_vec)
            
            if similarity >= threshold:
                # Return entry without the embedding list to keep it clean
                result_entry = {key: val for key, val in entry.items() if key != 'embedding'}
                result_entry['similarity'] = float(similarity)
                results.append(result_entry)

        # Sort by similarity descending
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:k]
