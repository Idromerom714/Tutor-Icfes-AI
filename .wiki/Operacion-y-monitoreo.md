# Operación y monitoreo

## Indicadores clave (KPIs)

- Tasa de respuestas exitosas por materia.
- Latencia promedio por etapa: embeddings, Pinecone, LLM.
- Errores por proveedor (OpenRouter, OpenAI, Pinecone, Supabase).
- Consumo de créditos por estudiante y por cuenta padre.
- Volumen de chats creados por día.

## Runbook de operación

### Verificación diaria

1. Confirmar disponibilidad de Supabase y estado de tablas críticas.
2. Validar conectividad con Pinecone e integridad de namespaces.
3. Ejecutar consulta de prueba end-to-end (pregunta de control).
4. Revisar consumo y límites de OpenRouter/OpenAI.

### Verificación semanal

1. Revisar tendencias de latencia y tasa de error.
2. Verificar crecimiento de `historial_chats` y estrategia de retención.
3. Auditar eventos de seguridad (intentos fallidos, bloqueos).

## Manejo de incidentes

### Síntoma: respuestas vacías o errores del tutor

- Validar `OPENROUTER_API_KEY` y estado del proveedor.
- Revisar logs de `core/ai_engine.py`.
- Probar fallback con otra materia/entrada sin imagen.

### Síntoma: sin contexto en respuestas (RAG)

- Verificar `PINECONE_API_KEY` y `PINECONE_INDEX_NAME`.
- Confirmar que el namespace tenga vectores.
- Revisar proceso de ingesta de documentos.

### Síntoma: fallos de persistencia

- Validar credenciales de Supabase y permisos.
- Confirmar disponibilidad de RPC `descontar_creditos`.
- Revisar errores en operaciones de `core/database.py`.

## Backups y recuperación

- Exportar periódicamente `padres`, `estudiantes`, `historial_chats`, `consentimientos`.
- Definir retención de backups (mínimo 30 días).
- Probar restauración parcial al menos una vez por trimestre.

## Observabilidad recomendada

- Log estructurado con `request_id` por sesión.
- Dashboards por proveedor externo (latencia y errores).
- Alertas para:
	- Error rate > 5% en 15 minutos.
	- Latencia p95 > umbral definido.
	- Fallas consecutivas de conexión a proveedor.
