# Datos y seguridad

## Datos almacenados
Tabla `perfiles` en Supabase:
- email
- pin
- plan
- preguntas_usadas
- imagenes_usadas
- ultima_fecha

## Seguridad basica
- No versionar `.streamlit/secrets.toml` ni `.env`.
- Rotar llaves si se sospecha filtracion.
- Limitar el acceso a Supabase con politicas (RLS).

## Consideraciones de privacidad
- Las preguntas pueden contener datos personales.
- Si se guardan logs, anonimizar el contenido sensible.

## Recomendaciones
- Validar formato de correo y PIN en el frontend.
- Enmascarar PIN en interfaces administrativas.
