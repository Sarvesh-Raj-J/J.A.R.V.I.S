#!/usr/bin/env python3
from modules.ai_assistant import AIAssistant
import logging

logging.basicConfig(level=logging.DEBUG)

print("Testing AIAssistant with 'wow'...")
ai = AIAssistant({})

# Test health check
print("\n1. Checking Ollama health...")
health = ai.check_ollama_health()
if health:
    print(f"   ✓ Ollama health: {health}")
else:
    print("   ✗ Ollama health check failed")

# Test query
print("\n2. Querying with 'wow'...")
response = ai.query("wow")
print(f"   Response: {response}")

print("\n3. Testing longer input...")
response2 = ai.query("can you play some music for me")
print(f"   Response: {response2}")
