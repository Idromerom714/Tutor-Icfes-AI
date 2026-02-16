# Operacion y monitoreo

## Indicadores clave
- Preguntas diarias por plan.
- Ratio de errores del API (OpenRouter).
- Latencia de busqueda en Pinecone.

## Manejo de errores
- `core/ai_engine.py` devuelve mensajes amigables.
- Registrar errores de API y tiempo de respuesta.

## Mantenimiento
- Revisar cuotas de OpenRouter/OpenAI.
- Verificar health de Pinecone.
- Asegurar que el reset diario corre (fecha en Supabase).

## Backups
- Exportar tabla `perfiles` periodicamente.
