import os
import pickle
import json
import numpy as np
import voyageai
from typing import List, Dict, Any
from tqdm import tqdm

class VectorDB:
    """
    """
    def __init__(self, name: str, dataset: str):
        """
        """
        self.client = voyageai.Client()
        self.name = name
        self.embeddings = []
        self.metadata = []
        self.db_path = f"./data/{name}/vector_db.pkl"
        # self.load_data(dataset)
        self.load_db()

    def load_data(self, dataset: List[Dict[str, Any]]):
        """
        """
        if self.embeddings and self.metadata:
            print("Vector database is already loaded. Skipping data loading.")
            return
        
        if os.path.exists(self.db_path):
            print("loading vector database from disk.")
            self.load_db()
            return
        
        texts_to_embed = []
        metadata = []
        total_chunks = sum(len(doc['chunks']) for doc in dataset)

        with tqdm(total=total_chunks, desc="Processing chunks") as pbar:
            for doc in dataset:
                for chunk in doc['chunks']:
                    texts_to_embed.append(chunk['content'])
                    metadata.append({
                        "doc_id": doc['doc_id'],
                        'original_uuid': doc['original_uuid'],
                        'chunk_id': chunk['chunk_id'],
                        'original_index': chunk['original_index'],
                        'content': chunk['content']
                    })
                    pbar.update(1)
        self._embed_and_store(texts_to_embed, metadata)
        self.save_db()

        print(f"Vector database loaded and saved. Total chunks processed: {len(texts_to_embed)}")

    def _embed_and_store(self, texts: List[str], data: List[Dict[str, Any]]):
        """
        """
        batch_size = 128
        with tqdm(total=len(texts), desc='Embedding chunks') as pbar:
            result = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i: i+batch_size]
                batch_result = self.client.embed(batch, model="voyage-2").embeddings
                result.extend(batch_result)
                pbar.update(len(batch))
        self.embeddings = result
        self.metadata = data
    
    def search(self, query: str, k: int = 20) -> List[Dict[str, Any]]:
        """
        """
        query_embedding = self.client.embed([query], model='voyage-2').embeddings[0]
        
        if not self.embeddings:
            raise ValueError("No data loaded in the vector database")
        
        similarities = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(similarities)[::-1][:k]

        top_results = []
        for idx in top_indices:
            result = {
                "metadata": self.metadata[idx],
                "similarity": float(similarities[idx])
            }
            top_results.append(result)
        return top_results

    def save_db(self):
        """
        """
        data = {
            "embeddings": self.embeddings,
            "metadata": self.metadata,
        }
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "wb") as file:
            pickle.dump(data, file)
    
    def load_db(self):
        """
        """
        if not os.path.exists(self.db_path):
            raise ValueError("Vector database file not found. Use load_data to create a new database.")
        
        with open(self.db_path, "rb") as file:
            data = pickle.load(file)

        self.embeddings = data['embeddings']
        self.metadata = data['metadata']
