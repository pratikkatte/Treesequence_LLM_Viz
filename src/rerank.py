import os
import time
import cohere
from typing import List, Dict, Any
from elastic import ElasticsearchBM25
from vector import VectorDB

class ReRankingAlgorithm:
    """
    """
    def __init__(self, k=10):
        """
        """
        # Vector DB

        # Elastic search
        vector_db = VectorDB("base_db", "data/tskit_large_chunk_1k.json")

        es_bm25 = ElasticsearchBM25()
        es_bm25.index_documents(vector_db.metadata)

        self.retrieval_db = es_bm25
        cohere_api_key = os.getenv("COHERE_API_KEY")
        self.co = cohere.Client(cohere_api_key)
        self.k = k
    
    def chunk_to_content(self, chunk: Dict[str, Any]) -> str:
        """
        """
        original_content = chunk['content']
        return f"{original_content}"

    def retrieve_rerank(self, query: str) -> List[Dict[str, Any]]:
        """
        """
        # Retrieve more results than we normally would
        semantic_results = self.retrieval_db.search(query, k=self.k*10)

        #Extract documents for rerankign, using the contextualized content
        documents = [self.chunk_to_content(res) for res in semantic_results]

        response = self.co.rerank(
            model='rerank-english-v3.0',
            query=query,
            documents=documents,
            top_n=self.k
        )
        time.sleep(0.1)

        final_results = []
        for r in response.results:
            original_result = semantic_results[r.index]
            final_results.append({
                "chunk": original_result['content'],
                "score": r.relevance_score
            })
        return final_results
        