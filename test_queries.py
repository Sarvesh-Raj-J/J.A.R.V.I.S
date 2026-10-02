#!/usr/bin/env python3
"""Test AIAssistant with multiple queries to verify Ollama integration"""

import sys
sys.path.insert(0, '.')
from modules.ai_assistant import AIAssistant

ai = AIAssistant({})

# Test multiple queries
test_queries = [
    "wow",
    "tell me a joke", 
    "what is the capital of france",
    "hello jarvis"
]

print("="*60)
print("Testing AIAssistant with Ollama Integration")
print("="*60)

for query in test_queries:
    print(f"\nQuery: '{query}'")
    response = ai.query(query)
    response_preview = response[:120] + "..." if len(response) > 120 else response
    print(f"Response: {response_preview}")
    print("-"*60)

print("\n✓ All tests completed!")
