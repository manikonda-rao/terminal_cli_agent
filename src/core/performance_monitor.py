import time

class PerformanceMonitor:
    def __init__(self):
        self.stats = {"cache_hits": 0, "cache_misses": 0, "parse_times": []}

    def record_cache_hit(self):
        self.stats["cache_hits"] += 1

    def record_cache_miss(self):
        self.stats["cache_misses"] += 1

    def record_time(self, start_time):
        elapsed = time.time() - start_time
        self.stats["parse_times"].append(elapsed)

    def report(self):
        total = self.stats["cache_hits"] + self.stats["cache_misses"]
        hit_rate = (self.stats["cache_hits"] / total * 100) if total > 0 else 0
        avg_time = sum(self.stats["parse_times"]) / len(self.stats["parse_times"]) if self.stats["parse_times"] else 0
        return {
            "hit_rate": f"{hit_rate:.2f}%",
            "avg_time": avg_time,
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"]
        }
