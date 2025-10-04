import time
import pytest
from src.core.intent_parser import IntentParser

def test_semantic_cache_hit():
    parser = IntentParser()
    text = "create a function to sort numbers"
    intent_type = list(parser.intent_patterns.keys())[0]  # pick any intent type

    # First call -> should compute and store in cache
    score1 = parser._calculate_semantic_confidence(text, intent_type)

    # Second call -> should hit cache
    score2 = parser._calculate_semantic_confidence(text, intent_type)

    assert score1 == score2
    assert (text, intent_type) in parser.semantic_cache.cache

def test_semantic_cache_ttl():
    parser = IntentParser(ttl=1)  # cache expires in 1 second
    text = "create a function to sort numbers"
    intent_type = list(parser.intent_patterns.keys())[0]

    score1 = parser._calculate_semantic_confidence(text, intent_type)

    time.sleep(2)  # wait for cache to expire
    score2 = parser._calculate_semantic_confidence(text, intent_type)

    # Even after expiry, score should still be valid, but cache entry is refreshed
    assert score1 == score2
    assert (text, intent_type) in parser.semantic_cache.cache
