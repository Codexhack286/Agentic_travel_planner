import os
import pytest

# Set dummy environment variables before any tests run
os.environ["GROQ_API_KEY"] = "gsk_test_key_placeholder"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["UNSPLASH_ACCESS_KEY"] = "test-unsplash-key"
os.environ["PASSPORT_API_KEY"] = "test-passport-key"
