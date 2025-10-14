from typing import List
import numpy as np


class SSR_Rater:
    def __init__(self, client, model: str = "text-embedding-3-small"):
        self.client = client
        self.model = model
        self._anchor_cache = {}

    async def _get_embedding(self, text: str) -> np.ndarray:
        response = await self.client.embeddings.create(input=[text], model=self.model)
        return np.array(response.data[0].embedding)

    async def _get_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        response = await self.client.embeddings.create(input=texts, model=self.model)
        return [np.array(item.embedding) for item in response.data]

    def _cosine_similarity(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        return np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )

    async def _get_or_cache_anchor_embeddings(
        self, anchor_statements: List[str]
    ) -> List[np.ndarray]:
        cache_key = tuple(anchor_statements)

        if cache_key not in self._anchor_cache:
            self._anchor_cache[cache_key] = await self._get_embeddings_batch(
                anchor_statements
            )

        return self._anchor_cache[cache_key]

    async def get_likert_distribution(
        self, text: str, anchor_statements: List[str], beta: float = 1.0
    ) -> np.ndarray:
        response_embedding = await self._get_embedding(text)
        anchor_embeddings = await self._get_or_cache_anchor_embeddings(
            anchor_statements
        )

        similarities = np.array(
            [
                self._cosine_similarity(response_embedding, anchor_embedding)
                for anchor_embedding in anchor_embeddings
            ]
        )

        similarities -= similarities.min()
        similarities **= beta

        pmf = similarities / similarities.sum()

        return pmf
