"""
Fixtures globales para tests.
"""

from unittest.mock import MagicMock
import pytest


@pytest.fixture(autouse=True)
def mock_streamlit_and_supabase(monkeypatch):
    """Mock de streamlit.secrets y supabase.create_client para evitar dependencias reales."""
    import streamlit as st
    import supabase

    dummy_secrets = {
        "SUPABASE_URL": "http://localhost",
        "SUPABASE_KEY": "test",
        "OPENROUTER_API_KEY": "test",
        "PINECONE_API_KEY": "test",
        "PINECONE_INDEX_NAME": "test-index",
        "OPENAI_API_KEY": "test",
    }

    monkeypatch.setattr(st, "secrets", dummy_secrets, raising=False)
    monkeypatch.setattr(supabase, "create_client", MagicMock(return_value=MagicMock()), raising=False)

    yield
