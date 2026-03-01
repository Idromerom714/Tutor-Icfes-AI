# Visión y alcance

## Objetivo

Ofrecer un tutor conversacional especializado en ICFES Saber 11, con enfoque socrático y respaldo en contexto recuperado desde fuentes documentales. El objetivo es mejorar comprensión, razonamiento y autonomía del estudiante.

## Alcance funcional actual

- Autenticación por correo + PIN hasheado.
- Registro padre/tutor y estudiantes asociados.
- Consulta por materia con RAG y modelos LLM especializados.
- Soporte de imágenes para análisis de ejercicios.
- Persistencia de historial de chats por estudiante y materia.
- Exportación de conversación a PDF.
- Gestión de créditos por consumo.

## Fuera de alcance (versión actual)

- Pasarela de pagos integrada.
- Panel administrativo completo con UX dedicada.
- Analítica pedagógica avanzada con recomendaciones automáticas.

## Principios de producto

- Respuestas guiadas (no dar la solución directa de inmediato).
- Enfoque por competencias ICFES.
- Transparencia en consumo de créditos.
- Trazabilidad y seguridad de datos.

## Prioridades de evolución

1. Unificar scripts legacy al modelo `padres/estudiantes`.
2. Centralizar configuración (`.env` vs `st.secrets`).
3. Adaptar ingesta de PDFs para ejecución local (sin dependencia de Colab).
