import re

class PatternOptimizer:
    def __init__(self, patterns_dict):
        # Precompile regex patterns for speed
        self.optimized_patterns = {
            intent: [re.compile(p, re.IGNORECASE) for p in patterns]
            for intent, patterns in patterns_dict.items()
        }
        self.usage_counter = {intent: 0 for intent in patterns_dict}

    def get_patterns(self, intent_type):
        # Order patterns by frequency of matches
        return sorted(
            self.optimized_patterns[intent_type],
            key=lambda pat: self.usage_counter[intent_type],
            reverse=True
        )

    def record_usage(self, intent_type):
        self.usage_counter[intent_type] += 1
