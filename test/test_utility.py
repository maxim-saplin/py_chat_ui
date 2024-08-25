import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from logic.utility import get_tokenizer, num_tokens_from_messages
from logic import env_vars

def test_get_tokenizer():
    tokenizer = get_tokenizer(env_vars.TokenizerKind.CL100K_BASE)
    assert tokenizer is not None

    with pytest.raises(ValueError):
        get_tokenizer("invalid_tokenizer_kind")

def test_num_tokens_from_messages():
    messages = [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm fine, thank you!"}
    ]
    tokenizer = get_tokenizer(env_vars.TokenizerKind.CL100K_BASE)
    num_tokens = num_tokens_from_messages(messages, tokenizer)
    assert num_tokens > 0
