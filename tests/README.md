# Suite de Tests - Tutor ICFES

## Resumen

Suite de tests completamente renovada (marzo 2026) alineada con el estado actual del código.

**Resultado actual:** ✅ **77 tests passed** (64 warnings de deprecación en fpdf2, sin impacto funcional)

## Archivos de Test

### `test_auth.py` (7 tests)
- Hasheo de PIN con bcrypt
- Verificación de PIN contra hash
- Manejo de caracteres especiales y case sensitivity

### `test_database.py` (15 tests)
- `obtener_datos_usuario()`: obtener padres desde Supabase
- `descontar_energia()`: llamadas al RPC `descontar_creditos`
- `guardar_o_actualizar_chat()`: inserción y actualización de chats
- `registrar_intento_fallido()` y `resetear_intentos()`: control de acceso
- `obtener_estudiante()`: relación padre-estudiante
- `obtener_ultimo_diagnostico()`: último resultado diagnóstico por estudiante
- `guardar_diagnostico_estudiante()`: persistencia de resultados
- `listar_diagnosticos_estudiante()`: historial de progreso semanal (últimas mediciones)

### `test_rag_search.py` (6 tests)
- `buscar_contexto_icfes()`: búsqueda vectorial en Pinecone
- Namespace correcto por materia
- Embeddings de 1536 dimensiones (text-embedding-3-small)
- Concatenación de resultados

### `test_ai_engine.py` (18 tests)
- Selección de modelos por materia:
  - Sociales/Lectura Crítica → Grok
  - Matemáticas sin imagen → DeepSeek
  - Matemáticas/Física con imagen → Gemini
- Validación del prompt socrático
- Manejo del historial de conversación
- Inyección de contexto diagnóstico para personalización pedagógica
- Modulación del estilo pedagógico por nivel recomendado (básico/intermedio/avanzado)
- Manejo de errores de API
- `generar_titulo_chat()`: generación de títulos

### `test_diagnostic.py` (12 tests)
- `obtener_preguntas_diagnostico()`: tamaño y validación de rango (10-15)
- Banco escalado: mínimo 100 variantes por competencia
- Verificación de diversidad semántica en variantes
- `evaluar_diagnostico()`: puntaje global y recomendaciones
- `obtener_materia_prioritaria()`: selección automática de materia débil
- `generar_preguntas_recomendadas()`: prompts sugeridos por tema
- `generar_plan_semanal()`: plan de estudio por días
- `diagnostico_requiere_renovacion()`: reactivación semanal cada 7 días
- Calibración de dificultad objetivo por materia

### `test_pdf_generator.py` (19 tests)
- `generar_pdf_estudio()`: generación de PDFs
- `limpiar_contenido()`: limpieza de markdown y LaTeX
- `sanitizar_para_pdf()`: preservación de acentos/ñ y sanitización
- Manejo de emojis, fórmulas y textos largos

## Ejecución

### Comando básico
```bash
pytest
```

### Con salida detallada
```bash
pytest -v
```

### Solo un archivo
```bash
pytest tests/test_auth.py -v
```

### Solo una clase de tests
```bash
pytest tests/test_database.py::TestIntentosFallidos -v
```

### Con cobertura
```bash
pytest --cov=core --cov-report=html
```

## Configuración

El archivo `pytest.ini` establece:
- `pythonpath = .` (para imports relativos)
- `testpaths = tests` (directorio de tests)
- `addopts = -v --tb=short` (salida verbosa y trazas cortas)

## Fixtures Globales (conftest.py)

El fixture `mock_streamlit_and_supabase` se aplica automáticamente a todos los tests y mockea:
- `streamlit.secrets` con valores dummy
- `supabase.create_client()` para evitar conexiones reales
- Incluye `SUPABASE_SERVICE_KEY` (requerido por `core/database.py`)

## Diferencias con la Suite Anterior

### Eliminados
- `test_ai.py` - supuestos obsoletos sobre RAG
- Tests desalineados de selección de modelos

### Actualizados
- Todos los tests de database ahora usan `supabase_admin` correctamente
- Tests de AI engine reflejan la lógica actual de selección de modelos
- Tests de RAG validados contra la implementación real
- Se agregó cobertura para diagnóstico inicial/semanal y seguimiento de progreso
- Se agregó cobertura para banco expandido de 100 variantes y dificultad adaptativa

## Notas

- Los warnings de deprecación de fpdf2 son conocidos y no afectan funcionalidad
- Todos los tests usan mocking para evitar dependencias externas (Supabase, Pinecone, OpenRouter)
- Para tests de integración reales, configurar variables de entorno reales y usar `pytest -m integration` (no implementado aún)

## Próximos Pasos

1. Agregar tests de integración con datos reales (marcados con `@pytest.mark.integration`)
2. Implementar tests para `pages/registro.py`
3. Agregar cobertura mínima del 80%
4. Agregar tests de performance para RAG
