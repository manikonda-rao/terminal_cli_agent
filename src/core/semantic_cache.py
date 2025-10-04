import time
from typing import Optional


class SemanticCache:
    """Simple semantic cache with optional TTL and LRU-style trimming."""
    def __init__(self, max_size: int = 500, ttl: Optional[int] = None):
        self.cache = {}  # key -> (score, expires_at)
        self.max_size = max_size
        self.ttl = ttl

    def _purge_expired(self):
        if self.ttl is None:
            return
        now = time.time()
        keys_to_delete = [k for k, (_, exp) in self.cache.items() if exp is not None and exp < now]
        for k in keys_to_delete:
            self.cache.pop(k, None)

    def get(self, text, intent_type):
        self._purge_expired()
        key = (text, intent_type)
        val = self.cache.get(key)
        if not val:
            return None
        score, expires_at = val
        return score

    def set(self, text, intent_type, score):
        # Trim if necessary
        if len(self.cache) >= self.max_size:
            try:
                self.cache.pop(next(iter(self.cache)))
            except StopIteration:
                pass
        key = (text, intent_type)
        expires_at = time.time() + self.ttl if self.ttl is not None else None
        self.cache[key] = (score, expires_at)
