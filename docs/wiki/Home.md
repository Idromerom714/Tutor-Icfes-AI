# Wiki - Tutor-Icfes-AI

Bienvenido a la wiki técnica y operativa del proyecto. Esta documentación está alineada con la versión actual de la aplicación (marzo 2026): arquitectura por módulos `core/`, modelo de datos `padres/estudiantes`, RAG por materia y flujo de créditos.

## Páginas principales

- [Visión y alcance](Vision-y-alcance.md)
- [Arquitectura y flujo](Arquitectura-y-flujo.md)
- [Instalación y configuración](Instalacion-y-configuracion.md)
- [Datos y seguridad](Datos-y-seguridad.md)
- [Operación y monitoreo](Operacion-y-monitoreo.md)
- [FAQ](FAQ.md)

## Mapa rápido del código

- Punto de entrada: [app.py](https://github.com/Idromerom714/Tutor-Icfes-AI/blob/main/app.py)
- Presentación y registro: [pages/presentacion.py](https://github.com/Idromerom714/Tutor-Icfes-AI/blob/main/pages/presentacion.py)
- Motor de IA: [core/ai_engine.py](https://github.com/Idromerom714/Tutor-Icfes-AI/blob/main/core/ai_engine.py)
- RAG: [core/rag_search.py](https://github.com/Idromerom714/Tutor-Icfes-AI/blob/main/core/rag_search.py)
- Base de datos: [core/database.py](https://github.com/Idromerom714/Tutor-Icfes-AI/blob/main/core/database.py)
- Autenticación: [core/auth.py](https://github.com/Idromerom714/Tutor-Icfes-AI/blob/main/core/auth.py)
- PDF: [core/pdf_generator.py](https://github.com/Idromerom714/Tutor-Icfes-AI/blob/main/core/pdf_generator.py)
- Scripts: [scripts/](https://github.com/Idromerom714/Tutor-Icfes-AI/tree/main/scripts)

## Estado actual

- Aplicación principal operativa con login, chat, historial y exportación PDF.
- Registro inicial de padre/tutor con consentimiento en `pages/presentacion.py`.
- Registro de hijos posterior a la activación, desde el panel del padre en `app.py`.
- Persistencia de chats y créditos en Supabase.
- RAG activo con OpenAI Embeddings + Pinecone por `namespace` de materia.
- Suite de pruebas renovada: 57 tests en verde.

## Navegación recomendada

1. Si es tu primera vez: empieza por [Visión y alcance](Vision-y-alcance.md).
2. Si vas a desarrollar: sigue con [Instalación y configuración](Instalacion-y-configuracion.md).
3. Si vas a operar producción: revisa [Operación y monitoreo](Operacion-y-monitoreo.md).
