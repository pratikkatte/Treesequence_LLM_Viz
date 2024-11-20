import os
import json
from typing import List, Dict, Any
from tqdm import tqdm
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

class ElasticsearchBM25:
    """
    """
    def __init__(self, index_name: str = "contextual_bm25_index"):
        self.es_client = Elasticsearch("http://localhost:9200", api_key="TGhxdk1aTUI1WG0yUndmTWJaRkk6NE9VWHRwUWVSaW1tU2VNNnozQlZvQQ==")
        self.index_name = index_name
        self.create_index() # create indexing

    def create_index(self):
        """
        """
        index_settings = {
            "settings": {
                "analysis": {"analyzer": {"default": {"type": "english"}}},
                "similarity": {"default": {"type": "BM25"}},
                "index.queries.cache.enabled": False  # Disable query cache
            },
            "mappings": {
                "properties": {
                    "content": {"type": "text", "analyzer": "english"},
                    "contextualized_content": {"type": "text", "analyzer": "english"},
                    "doc_id": {"type": "keyword", "index": False},
                    "chunk_id": {"type": "keyword", "index": False},
                    "original_index": {"type": "integer", "index": False},
                }
            },
        }
        if not self.es_client.indices.exists(index=self.index_name):
            self.es_client.indices.create(index=self.index_name, body=index_settings)
            print(f"Created index: {self.index_name}")

    def index_documents(self, documents: List[Dict[str, Any]]):
        """
        """
        actions = [
            {
                "_index": self.index_name,
                "_source": {
                    "content": doc["content"],
                    "doc_id": doc["doc_id"],
                    "chunk_id": doc["chunk_id"],
                    "original_index": doc["original_index"],
                },
            }
            for doc in documents
        ]
        success, _ = bulk(self.es_client, actions)
        self.es_client.indices.refresh(index=self.index_name)
        return success

    def search(self, query: str, k: int = 20) -> List[Dict[str, Any]]:
        """
        """
        self.es_client.indices.refresh(index=self.index_name)  # Force refresh before each search
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields":["content"],
                }
            },
            "size": k,
        }
        response = self.es_client.search(index=self.index_name, body=search_body)
        return [
            {
                "doc_id": hit["_source"]["doc_id"],
                "original_index": hit["_source"]["original_index"],
                "content": hit["_source"]["content"],
                "score": hit["_score"],
            }
            for hit in response["hits"]["hits"]
        ]