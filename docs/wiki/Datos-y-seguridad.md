# Datos y seguridad

## Modelo de datos actual

La aplicación usa Supabase con las tablas principales:

- `padres`: credenciales (PIN hasheado), plan, estado y créditos.
- `estudiantes`: estudiantes vinculados al padre/tutor.
- `historial_chats`: conversaciones por materia en formato JSON.
- `consentimientos`: trazabilidad de aceptación de políticas.

> Referencia técnica: [core/database.py](https://github.com/Idromerom714/Tutor-Icfes-AI/blob/main/core/database.py)

## Datos sensibles tratados

- Correo electrónico del tutor.
- PIN de acceso (guardado como hash bcrypt, nunca en texto plano).
- Contenido de conversaciones de estudio.
- Evidencia de consentimiento de tratamiento de datos.

## Seguridad aplicada

- Hash de PIN con bcrypt en [core/auth.py](https://github.com/Idromerom714/Tutor-Icfes-AI/blob/main/core/auth.py).
- Uso de `SUPABASE_SERVICE_KEY` solo para operaciones administrativas necesarias.
- Separación entre clave pública (`SUPABASE_KEY`) y clave de servicio.
- Recomendación de RLS activa para accesos no administrativos.

## Reglas operativas recomendadas

1. No versionar `.streamlit/secrets.toml` ni `.env`.
2. Rotar claves API y claves de Supabase ante sospecha de filtración.
3. Limitar acceso de operadores al mínimo privilegio.
4. Auditar periódicamente logs de acceso y modificaciones críticas.

## Privacidad y cumplimiento

- Evitar almacenar datos innecesarios en prompts.
- En reportes o analítica, anonimizar contenido sensible.
- Mantener versión de política en `consentimientos.version_politica`.
- Registrar fecha y evidencia de aceptación.

## Función crítica de negocio

La gestión de créditos se realiza mediante RPC (`descontar_creditos`) para mantener atomicidad y consistencia transaccional.

## Checklist de seguridad

- [ ] Secrets cargados solo en entorno seguro.
- [ ] RLS revisada en tablas expuestas.
- [ ] Rotación de llaves definida.
- [ ] Backups regulares de tablas críticas.
