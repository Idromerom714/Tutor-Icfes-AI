# FAQ

## No puedo iniciar sesión

- Verifica correo y PIN.
- Confirma que el padre/tutor exista en la tabla `padres`.
- Si hay bloqueos por intentos fallidos, valida estado de cuenta.

## El tutor no responde

- Revisa `OPENROUTER_API_KEY`.
- Verifica conectividad a `https://openrouter.ai`.
- Comprueba que la materia esté configurada correctamente.

## La búsqueda no trae contexto (RAG)

- Revisa `PINECONE_API_KEY` y `PINECONE_INDEX_NAME`.
- Confirma que el namespace exista y tenga vectores (`matematicas`, `fisica`, `sociales`, `lectura_critica`, `ingles`).
- Verifica que OpenAI embeddings esté respondiendo correctamente.

## Se agotaron los créditos

- El sistema usa saldo de créditos, no reset diario automático.
- Revisa `creditos_totales` en `padres`.
- Valida RPC `descontar_creditos` y política de recarga del plan.

## No puedo exportar el PDF

- Verifica que el chat tenga mensajes válidos.
- Reintenta desde una conversación guardada.
- Revisa errores en `core/pdf_generator.py`.

## El registro no crea correctamente al estudiante

- Verifica inserciones en `padres`, `estudiantes` y `consentimientos`.
- Comprueba que la clave de servicio de Supabase esté disponible cuando aplique.

## ¿Dónde veo la documentación completa de tests?

- Revisa [tests/README.md](https://github.com/Idromerom714/Tutor-Icfes-AI/blob/main/tests/README.md).
