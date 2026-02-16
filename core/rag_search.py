import streamlit as st
from openai import OpenAI
from pinecone import Pinecone # Importación corregida

def buscar_contexto_icfes(query, materia):
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    index = pc.Index(st.secrets["PINECONE_INDEX_NAME"])
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    res = client.embeddings.create(input=[query], model="text-embedding-3-small")
    vector_busqueda = res.data[0].embedding

    busqueda = index.query(
        vector=vector_busqueda,
        top_k=3,
        include_metadata=True,
        namespace=materia.lower()
    )
    return "\n\n".join([m['metadata']['texto'] for m in busqueda['matches']])