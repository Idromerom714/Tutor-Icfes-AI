# Changelog

Registro de cambios significativos en el proyecto Tutor-Icfes-AI.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

## [Unreleased]

### Agregado - 2026-03-07

#### Diagnóstico y personalización pedagógica
- 🧭 Nuevo módulo `core/diagnostic.py` con:
  - Banco de preguntas tipo ICFES (10-15, configuración actual en 12)
  - Evaluación por materia y temas a reforzar
  - Recomendaciones automáticas de refuerzo
  - Selección de materia prioritaria según menor desempeño
  - Generación de preguntas sugeridas por tema
  - Generación de plan semanal de estudio
  - Regla de renovación diagnóstica cada 7 días
- 🧠 `core/ai_engine.py` ahora inyecta el perfil diagnóstico en el prompt del sistema y en el contexto del turno para que el tutor enfoque competencias débiles.
- 📈 Sidebar en `app.py` ampliado con:
  - Plan de refuerzo
  - Preguntas recomendadas para iniciar sesión de estudio
  - Plan semanal sugerido
  - Progreso semanal (últimas 4 mediciones) con tendencia
  - Indicador de nivel recomendado por materia (básico/intermedio/avanzado)

#### Diagnóstico avanzado
- 🧱 Banco de preguntas escalado a **100 variantes por competencia** con diversidad semántica.
- 🎚️ Calibración de dificultad por competencia y por materia (`basico`, `intermedio`, `avanzado`) según desempeño previo.
- 🧭 El motor IA adapta el estilo de tutoría por nivel recomendado para cada sesión.

#### Persistencia en base de datos
- 🗄️ Nuevas operaciones en `core/database.py` para diagnóstico:
  - `obtener_ultimo_diagnostico()`
  - `guardar_diagnostico_estudiante()`
  - `listar_diagnosticos_estudiante()`
- 🔐 Documentado SQL para tabla `diagnosticos_estudiante` con índices y lineamientos RLS (incluyendo políticas estrictas por padre/estudiante).

#### Flujo de aplicación
- 🔁 El login ahora valida vigencia del diagnóstico:
  - Si está vigente, carga perfil y prioriza materia automáticamente.
  - Si venció (7 días), exige diagnóstico semanal y compara progreso con la medición anterior.

#### Tests y documentación
- ✅ Suite ampliada a **77 tests** (100% éxito):
  - `test_diagnostic.py` agregado (8 tests)
  - `test_ai_engine.py` ampliado para contexto diagnóstico
  - `test_database.py` ampliado para historial de diagnósticos
- 📝 Documentación actualizada en `README.md` y `tests/README.md` para reflejar diagnóstico semanal, personalización y seguimiento.

### Agregado - 2026-03-01

#### Documentación
- ✨ README completamente reescrito con:
  - Badges de estado (Python, Streamlit, Tests, Licencia)
  - Tabla de contenidos navegable
  - Sección de características principales con emojis
  - Diagrama ASCII de flujo de arquitectura
  - Tabla de stack tecnológico con enlaces
  - Tabla de estructura de datos Supabase
  - Sección de despliegue con ejemplo Docker
  - Roadmap de mejoras priorizado
- 📋 `tests/README.md` - Documentación completa de la suite de tests
- 📊 `CHANGELOG.md` - Este archivo

#### Suite de Tests
- 🧪 Suite completamente renovada: **57 tests** (100% éxito)
  - `test_auth.py` - 7 tests para autenticación bcrypt
  - `test_database.py` - 10 tests para operaciones Supabase
  - `test_rag_search.py` - 6 tests para búsqueda vectorial
  - `test_ai_engine.py` - 15 tests para motor de IA
  - `test_pdf_generator.py` - 19 tests para generación PDF
- ⚙️ `pytest.ini` - Configuración centralizada de pytest
- 🔧 `conftest.py` actualizado con `SUPABASE_SERVICE_KEY`

### Cambiado - 2026-03-01

#### Documentación
- 📝 README:
  - Estado del proyecto actualizado (suite de tests renovada)
  - Sección de pruebas actualizada (57 passed vs 40 passed/25 failed)
  - Limitaciones conocidas simplificadas y aclaradas
  - Scripts disponibles con descripciones detalladas
  - Sección "Ejecutar la app" dividida en desarrollo/producción

### Eliminado - 2026-03-01

#### Tests
- 🗑️ Tests obsoletos eliminados:
  - `test_ai.py` - supuestos antiguos sobre RAG
  - `test_recarga_creditos.py` - función inexistente
  - `test_historial_chats.py` - modelo desactualizado
  - `test_pdf_export.py` - duplicado de funcionalidad

### Corregido - 2026-03-01

#### Tests
- ✅ Mocking de `SUPABASE_SERVICE_KEY` en `conftest.py`
- ✅ Tests de selección de modelos alineados con lógica actual
- ✅ Tests de database usando `supabase_admin` correctamente
- ✅ Eliminados tests de funciones inexistentes

---

## Resumen de Impacto

### Antes (Suite antigua)
```
65 tests total
40 passed ✅
25 failed ❌ (39% tasa de fallo)
230 warnings
```

### Después (Suite actual)
```
77 tests total
77 passed ✅ (100% éxito)
0 failed ✅
64 warnings (solo deprecaciones fpdf2)
```

### Cobertura por Módulo

| Módulo | Tests | Descripción |
|--------|-------|-------------|
| `core/ai_engine.py` | 18 | Selección modelos, prompt, historial, errores, contexto diagnóstico y nivel pedagógico |
| `core/pdf_generator.py` | 19 | Generación PDF, limpieza markdown/LaTeX |
| `core/database.py` | 15 | CRUD usuarios, chats, créditos, intentos, diagnósticos |
| `core/auth.py` | 7 | Hashing/verificación bcrypt |
| `core/rag_search.py` | 6 | Búsqueda vectorial, embeddings |
| `core/diagnostic.py` | 12 | Diagnóstico, banco 100 variantes, dificultad, priorización y renovación |

---

## Próximas Tareas Sugeridas

### Alta Prioridad
- [ ] Migrar scripts legacy de `perfiles` a `padres/estudiantes`
- [ ] Centralizar configuración (unificar `.env` y `st.secrets`)
- [ ] Adaptar `scripts/upload_pdfs.py` para ejecución local

### Media Prioridad
- [ ] Agregar tests de integración (marcados `@pytest.mark.integration`)
- [ ] Implementar medición de cobertura con `pytest-cov`
- [ ] Generar documentación API automática

### Baja Prioridad
- [ ] Cache de embeddings frecuentes
- [ ] Telemetría y monitoreo
- [ ] Pipeline CI/CD automatizado
