# Instalacion y configuracion

## Requisitos
- Python 3.10+
- Supabase, Pinecone, OpenAI, OpenRouter

## Instalacion
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Secrets (Streamlit)
Crea `.streamlit/secrets.toml`:
```toml
OPENROUTER_API_KEY = "..."
OPENAI_API_KEY = "..."
PINECONE_API_KEY = "..."
PINECONE_INDEX_NAME = "icfes-index"
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "..."
```

## Variables para scripts
Crea `.env` (solo scripts):
```env
SUPABASE_URL=...
SUPABASE_KEY=...
```

## Ejecutar la app
```bash
streamlit run app.py --server.enableCORS false --server.enableXsrfProtection false
```

## Notas
- El modelo de chat esta en [core/ai_engine.py](../../core/ai_engine.py).
- La tabla `perfiles` debe existir en Supabase.
