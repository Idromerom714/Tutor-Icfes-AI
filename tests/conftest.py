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
        "SUPABASE_URL": "http://localhost:54321",
        "SUPABASE_KEY": "test-anon-key",
        "SUPABASE_SERVICE_KEY": "test-service-key",
        "OPENROUTER_API_KEY": "test-openrouter-key",
        "PINECONE_API_KEY": "test-pinecone-key",
        "PINECONE_INDEX_NAME": "icfes-index",
        "OPENAI_API_KEY": "test-openai-key",
    }

    monkeypatch.setattr(st, "secrets", dummy_secrets, raising=False)
    monkeypatch.setattr(supabase, "create_client", MagicMock(return_value=MagicMock()), raising=False)

    yield
