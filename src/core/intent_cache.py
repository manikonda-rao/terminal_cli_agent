import time
from collections import OrderedDict

class IntentCache:
    def __init__(self, max_size=500, ttl=300):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl  # seconds

    def _is_expired(self, key):
        if key not in self.cache:
            return True
        _, expiry = self.cache[key]
        return time.time() > expiry

    def get(self, key):
        if key in self.cache and not self._is_expired(key):
            value, _ = self.cache.pop(key)
            # re-insert to mark as most recently used
            self.cache[key] = (value, time.time() + self.ttl)
            return value
        return None

    def set(self, key, value):
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)  # remove oldest
        self.cache[key] = (value, time.time() + self.ttl)

    def stats(self):
        return {"size": len(self.cache), "capacity": self.max_size}
