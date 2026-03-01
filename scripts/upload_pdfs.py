#Este es el script que se encarga de subir los archivos PDF a la base de datos. Se ejecuta cada vez que se agrega un nuevo PDF a la carpeta "pdfs" y se encarga de extraer el texto del PDF y guardarlo en la base de datos junto con el nombre del archivo.
#El script también se encarga de dividir el texto extraído en chunks de 1000 caracteres con un overlap de 200 caracteres para evitar que el contexto importante quede partido entre dos chunks. Cada chunk se guarda en la base de datos junto con el nombre del archivo y el embedding generado por el modelo text-embedding-3-small.
#Para ejecutar este script, es necesario tener las siguientes dependencias instaladas:
#- PyPDF2: para extraer el texto de los archivos PDF.
#- openai: para generar los embeddings de los chunks de texto.
#- pinecone: para interactuar con la base de datos Pinecone.
#se recomienda ejecutar este script en un entorno de Google Colab para facilitar la gestión de las dependencias y el acceso a los archivos PDF almacenados en Google Drive.

import os
import hashlib
from PyPDF2 import PdfReader
from openai import OpenAI
from pinecone import Pinecone
from google.colab import drive
from google.colab import userdata

# --- CONFIGURACIÓN ---
os.environ["OPENAI_API_KEY"] = userdata.get('OPENAI_API_KEY') # Retrieve API key from Colab secrets
pc = Pinecone(api_key=userdata.get('PINECONE_API_KEY')) # Retrieve Pinecone API key from Colab secrets
index = pc.Index("icfes-index")
client = OpenAI()

drive.mount('/content/drive')


def chunk_texto(texto, chunk_size=1000, overlap=200):
    """
    Divide el texto en chunks con overlap (solapamiento).
    El overlap evita que el contexto importante quede partido entre dos chunks.
    """
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fin = inicio + chunk_size
        chunks.append(texto[inicio:fin])
        inicio += chunk_size - overlap  # retrocede 'overlap' caracteres para el siguiente chunk
    return chunks

def procesar_y_subir_pdf(carpeta, materia):
    for archivo_nombre in os.listdir(carpeta):
        ruta_completa_archivo = os.path.join(carpeta, archivo_nombre)

        if not os.path.isfile(ruta_completa_archivo):
            print(f"⏩ Saltando '{ruta_completa_archivo}' porque no es un archivo.")
            continue

        if not archivo_nombre.lower().endswith(".pdf"):
            print(f"⏩ Saltando '{archivo_nombre}' porque no es un PDF.")
            continue

        print(f"📖 Leyendo: {ruta_completa_archivo}...")

        try:
            reader = PdfReader(ruta_completa_archivo)
        except Exception as e:
            print(f"❌ No se pudo leer '{archivo_nombre}': {e}")
            continue

        # Extraer texto manejando páginas que retornen None
        texto_completo = ""
        for page in reader.pages:
            texto_pagina = page.extract_text()
            if texto_pagina:
                texto_completo += texto_pagina + "\n"

        if not texto_completo.strip():
            print(f"⚠️  '{archivo_nombre}' no tiene texto extraíble (¿PDF escaneado?).")
            continue

        chunks = chunk_texto(texto_completo, chunk_size=1000, overlap=200)
        print(f"✂️  {len(chunks)} chunks generados. Creando embeddings...")

        vectores_para_subir = []

        # Sanitize materia for ASCII-only ID
        materia_ascii = materia.encode('ascii', 'ignore').decode('ascii')

        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            # ID único basado en el nombre del archivo + índice del chunk
            # Usar materia_ascii para cumplir con el requisito de Pinecone
            id_unico = f"{materia_ascii}_{hashlib.md5(archivo_nombre.encode()).hexdigest()[:8]}_{i}"

            try:
                res = client.embeddings.create(
                    input=[chunk],
                    model="text-embedding-3-small",
                    dimensions=1536
                )
                embedding = res.data[0].embedding
            except Exception as e:
                print(f"❌ Error en embedding del chunk {i} de '{archivo_nombre}': {e}")
                continue

            vectores_para_subir.append({
                "id": id_unico,
                "values": embedding,
                "metadata": {
                    "texto": chunk,
                    "materia": materia,
                    "archivo": archivo_nombre  # útil para saber de dónde vino el chunk
                }
            })

        # Upsert en lotes
        batch_size = 100
        for i in range(0, len(vectores_para_subir), batch_size):
            batch = vectores_para_subir[i:i + batch_size]
            try:
                index.upsert(vectors=batch)
                print(f"✅ Lote {i//batch_size + 1}: {len(batch)} vectores subidos de '{archivo_nombre}'")
            except Exception as e:
                print(f"❌ Error subiendo lote {i//batch_size + 1}: {e}")

        print(f"🎉 '{archivo_nombre}' procesado completamente.\n")


# --- EJECUCIÓN ---
procesar_y_subir_pdf("/content/temas", "Temas")