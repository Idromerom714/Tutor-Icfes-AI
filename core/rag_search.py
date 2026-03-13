import logging

import streamlit as st
from openai import OpenAI
from pinecone import Pinecone


logger = logging.getLogger(__name__)


def _get_secret(name):
    """Lee un secreto sin lanzar excepción cuando no existe."""
    try:
        return st.secrets[name]
    except Exception:
        return None

def buscar_contexto_icfes(query, materia):
    pinecone_api_key = _get_secret("PINECONE_API_KEY")
    pinecone_index_name = _get_secret("PINECONE_INDEX_NAME")
    openai_api_key = _get_secret("OPENAI_API_KEY")

    # Si falta configuración RAG, continuar sin contexto en vez de romper el chat.
    if not pinecone_api_key or not pinecone_index_name or not openai_api_key:
        return ""

    try:
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index(pinecone_index_name)
        client = OpenAI(api_key=openai_api_key)

        res = client.embeddings.create(input=[query], model="text-embedding-3-small")
        vector_busqueda = res.data[0].embedding

        busqueda = index.query(
            vector=vector_busqueda,
            top_k=3,
            include_metadata=True,
            namespace=materia.lower(),
        )

        textos = []
        for match in busqueda.get("matches", []):
            texto = match.get("metadata", {}).get("texto")
            if texto:
                textos.append(texto)

        return "\n\n".join(textos)
    except Exception as exc:
        logger.warning("RAG deshabilitado temporalmente por error en búsqueda: %s", exc)
        return ""