import streamlit as st
from openai import OpenAI
from pinecone import Pinecone

pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
index = pc.Index(st.secrets["PINECONE_INDEX_NAME"])
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def buscar_contexto_icfes(query):
    # 1. Convertir duda a números
    res = client.embeddings.create(
        input=[query],
        model="text-embedding-3-small"
    )
    vector_busqueda = res.data[0].embedding

    # 2. Buscar en Pinecone los 3 pedazos más relevantes
    busqueda = index.query(
        vector=vector_busqueda,
        top_k=3,
        include_metadata=True
    )
    
    # 3. Concatenar los textos encontrados
    contexto = "\n\n".join([m['metadata']['texto'] for m in busqueda['matches']])
    return contexto