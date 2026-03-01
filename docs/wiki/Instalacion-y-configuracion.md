# Instalación y configuración

## Requisitos

- Python 3.10+
- Cuenta y proyecto en Supabase
- Índice en Pinecone
- API keys de OpenRouter y OpenAI

## Instalación local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración de secretos (Streamlit)

Crea `.streamlit/secrets.toml`:

```toml
OPENROUTER_API_KEY = "..."
OPENAI_API_KEY = "..."
PINECONE_API_KEY = "..."
PINECONE_INDEX_NAME = "icfes-index"
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "..."
SUPABASE_SERVICE_KEY = "..."
```

> `SUPABASE_SERVICE_KEY` es necesaria para operaciones administrativas del flujo actual.

## Variables para scripts CLI

Crea `.env` (solo scripts legacy y utilidades):

```env
SUPABASE_URL=...
SUPABASE_KEY=...
```

## Ejecutar la app

Desarrollo:

```bash
streamlit run app.py
```

Producción controlada:

```bash
streamlit run app.py --server.enableCORS false --server.enableXsrfProtection false
```

## Checklist de arranque

1. Verificar acceso a Supabase (`padres`, `estudiantes`, `historial_chats`, `consentimientos`).
2. Verificar índice Pinecone y namespaces por materia.
3. Confirmar respuesta de OpenRouter en una consulta de prueba.
4. Confirmar generación de embeddings de OpenAI.

## Referencias

- Configuración principal: [README.md](https://github.com/Idromerom714/Tutor-Icfes-AI/blob/main/README.md)
- Motor IA: [core/ai_engine.py](https://github.com/Idromerom714/Tutor-Icfes-AI/blob/main/core/ai_engine.py)
- Conexión DB: [core/database.py](https://github.com/Idromerom714/Tutor-Icfes-AI/blob/main/core/database.py)
