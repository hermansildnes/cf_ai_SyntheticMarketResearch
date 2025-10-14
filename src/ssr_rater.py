from typing import List
import math
import os
import requests


class SSR_Rater:
    def __init__(self, model: str = "@cf/google/embeddinggemma-300m"):
        self.model = model
        self._anchor_cache = {}
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.auth_token = os.getenv("CLOUDFLARE_API_KEY")
        if not self.auth_token:
            raise ValueError("CLOUDFLARE_API_KEY environment variable is not set.")

    def _get_embedding(self, text: str) -> list:
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model}"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {"text": [text]}
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["result"]["embeddings"][0]

    def _cosine_similarity(
        self, embedding1: list, embedding2: list
    ) -> float:
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = math.sqrt(sum(a * a for a in embedding1))
        norm2 = math.sqrt(sum(b * b for b in embedding2))
        return dot_product / (norm1 * norm2)

    def get_likert_distribution(
        self, text: str, anchor_statements: List[str], beta: float = 1.0
    ) -> list:
        if tuple(anchor_statements) not in self._anchor_cache:
            self._anchor_cache[tuple(anchor_statements)] = [
                self._get_embedding(anchor) for anchor in anchor_statements
            ]

        response_embedding = self._get_embedding(text)
        anchor_embeddings = self._anchor_cache[tuple(anchor_statements)]

        similarities = [
            self._cosine_similarity(response_embedding, anchor_embedding)
            for anchor_embedding in anchor_embeddings
        ]

        min_similarity = min(similarities)
        similarities = [(sim - min_similarity) ** beta for sim in similarities]
        total = sum(similarities)

        return [sim / total for sim in similarities]
