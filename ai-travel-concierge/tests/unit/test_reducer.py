import pytest
from src.graphs.state.conversation_state import merge_messages

def test_merge_messages_empty():
    assert merge_messages([], []) == []
    assert merge_messages([], [{"role": "user", "content": "hi"}]) == [{"role": "user", "content": "hi"}]
    assert merge_messages([{"role": "user", "content": "hi"}], []) == [{"role": "user", "content": "hi"}]

def test_merge_messages_append():
    left = [{"role": "user", "content": "hello"}]
    right = [{"role": "assistant", "content": "hi"}]
    expected = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"}
    ]
    assert merge_messages(left, right) == expected

def test_merge_messages_no_duplication():
    # If the returned state includes the existing message list (a common behavior when nodes return full state)
    left = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"}
    ]
    right = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
        {"role": "user", "content": "next message"}
    ]
    expected = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
        {"role": "user", "content": "next message"}
    ]
    assert merge_messages(left, right) == expected

def test_merge_messages_exact_duplicate_ignored():
    left = [
        {"role": "user", "content": "hello"}
    ]
    right = [
        {"role": "user", "content": "hello"}
    ]
    # If right is identical to left, return left/right without duplicating
    assert merge_messages(left, right) == [{"role": "user", "content": "hello"}]

def test_merge_messages_consecutive_identicals_kept_if_interspersed():
    # If there is a conversation flow, consecutive identical user messages are preserved
    left = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"}
    ]
    right = [
        {"role": "user", "content": "hello"}
    ]
    expected = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
        {"role": "user", "content": "hello"}
    ]
    assert merge_messages(left, right) == expected
