import hashlib
import re
from typing import Dict, Any, List, Set

class DuplicateDetector:
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.seen_hashes: Set[str] = set()
        self.seen_token_sets: List[Set[str]] = []

    def _normalize(self, text: str) -> str:
        return re.sub(r"[^\w\s]", "", text.lower()).strip()

    def _hash_content(self, text: str) -> str:
        clean = self._normalize(text)
        return hashlib.sha256(clean.encode("utf-8")).hexdigest()

    def _tokenize(self, text: str) -> Set[str]:
        clean = self._normalize(text)
        return set(clean.split())

    def _jaccard_similarity(self, set_a: Set[str], set_b: Set[str]) -> float:
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        return intersection / float(union) if union > 0 else 0.0

    def is_duplicate(self, asset: Dict[str, Any]) -> bool:
        content = f"{asset.get('hook', '')} {asset.get('caption', '')}"
        content_hash = self._hash_content(content)

        if content_hash in self.seen_hashes:
            return True

        tokens = self._tokenize(content)
        for existing_tokens in self.seen_token_sets:
            sim = self._jaccard_similarity(tokens, existing_tokens)
            if sim >= self.similarity_threshold:
                return True

        return False

    def register_asset(self, asset: Dict[str, Any]):
        content = f"{asset.get('hook', '')} {asset.get('caption', '')}"
        content_hash = self._hash_content(content)
        self.seen_hashes.add(content_hash)
        self.seen_token_sets.append(self._tokenize(content))

    def reset(self):
        self.seen_hashes.clear()
        self.seen_token_sets.clear()
