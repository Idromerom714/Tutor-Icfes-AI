# Tutor-Icfes-AI

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/tests-57%20passed-success.svg)](tests/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Descripción General

**Tutor-Icfes-AI** es un asistente educativo inteligente diseñado para ayudar a estudiantes colombianos en su preparación para el examen ICFES Saber 11. A diferencia de un simple bot de preguntas y respuestas, este tutor implementa un **enfoque socrático**: guía al estudiante a través de preguntas y reflexiones para que descubra las respuestas por sí mismo, promoviendo el aprendizaje profundo.

El sistema combina tecnologías de vanguardia en inteligencia artificial:

- **Recuperación Aumentada de Generación (RAG)**: Búsqueda semántica en documentos oficiales del ICFES para proporcionar contexto preciso y actualizado
- **Modelos de lenguaje especializados**: Selección inteligente entre Grok, DeepSeek y Gemini según el tipo de consulta
- **Análisis de imágenes**: Capacidad de interpretar fotos de ejercicios, gráficas o problemas matemáticos
- **Persistencia total**: Historial completo de conversaciones y exportación a PDF

### Para quién es este proyecto

- **Estudiantes de 10° y 11°**: Preparación estructurada para el ICFES en 5 materias clave
- **Padres y tutores**: Plataforma para gestionar el aprendizaje de múltiples estudiantes
- **Instituciones educativas**: Sistema escalable con control de créditos y monitoreo de uso

## 📑 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Stack Tecnológico](#-stack-tecnológico)
- [Configuración e Instalación](#-configuración-e-instalación)
- [Estructura de Datos](#-estructura-de-datos)
- [Uso y Ejecución](#-uso-y-ejecución)
- [Scripts Disponibles](#-scripts-disponibles)
- [Pruebas](#-pruebas)
- [Despliegue](#-despliegue)
- [Wiki y Documentación](#-wiki-y-documentación)
- [Roadmap](#-roadmap)

## ✨ Características Principales

### Experiencia del estudiante

- **🎓 Método socrático**: El tutor no da respuestas directas; formula preguntas guiadas para estimular el pensamiento crítico
- **📚 Asistencia por materia**: Soporte especializado en:
  - Matemáticas (razonamiento lógico-cuantitativo)
  - Física (análisis de fenómenos y resolución de problemas)
  - Ciencias Sociales (comprensión histórica y contextual)
  - Lectura Crítica (análisis textual y argumentación)
  - Inglés (comprensión lectora y uso del idioma)
- **📸 Análisis de imágenes**: Sube fotos de ejercicios, gráficas o problemas; el sistema las interpreta automáticamente
- **💬 Memoria contextual**: El tutor recuerda la conversación completa dentro de cada sesión
- **📄 Exportación PDF**: Descarga resúmenes limpios de estudio con todo el historial de la conversación
- **🔄 Historial persistente**: Acceso a todas las conversaciones anteriores organizadas por materia

### Experiencia del padre/tutor

- **👨‍👩‍👧 Gestión familiar**: Registro y monitoreo de múltiples estudiantes desde una cuenta
- **⚡ Sistema de créditos flexible**: Planes básico, estándar y familia con recarga automática
- **📊 Transparencia total**: Visualización del uso de créditos por estudiante y materia
- **🔐 Seguridad robusta**: Autenticación con PIN, bloqueo por intentos fallidos, encriptación bcrypt

### Inteligencia artificial avanzada

- **🧠 Selección automática de modelo**:
  - **Grok** (x-ai/grok-4.1-fast): Para Ciencias Sociales y Lectura Crítica (razonamiento analítico)
  - **DeepSeek** (deepseek/deepseek-v3.2): Para Matemáticas y Física (lógica formal)
  - **Gemini** (google/gemini-2.0-flash-001): Para análisis de imágenes con capacidad visual
- **📖 RAG especializado**: Cada materia tiene su propio namespace en Pinecone con documentos oficiales del ICFES
- **🎯 Embeddings semánticos**: OpenAI text-embedding-3-small (1536 dimensiones) para búsqueda contextual precisa

## 🏗️ Arquitectura del Sistema

### Visión general

Tutor-Icfes-AI sigue una arquitectura de **tres capas** con desacoplamiento entre presentación, lógica de negocio y persistencia:

```
┌────────────────────────────────────────────────────────────┐
│                    PRESENTACIÓN (Streamlit)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   app.py     │  │ registro.py  │  │   pages/     │     │
│  │  (Chat UI)   │  │ (Sign-up)    │  │ (Historial)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────────┬────────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────────┐
│                    LÓGICA DE NEGOCIO (core/)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   auth.py    │  │ database.py  │  │ ai_engine.py │     │
│  │ (bcrypt PIN) │  │ (Supabase)   │  │ (LLM logic)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │rag_search.py │  │pdf_generator │                        │
│  │ (Embeddings) │  │   .py        │                        │
│  └──────────────┘  └──────────────┘                        │
└───────────────────────────┬────────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────────┐
│                  SERVICIOS EXTERNOS (APIs)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Supabase    │  │  Pinecone    │  │ OpenRouter   │     │
│  │ (Postgres)   │  │ (Vectores)   │  │  (LLMs)      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐                                          │
│  │   OpenAI     │                                          │
│  │ (Embeddings) │                                          │
│  └──────────────┘                                          │
└────────────────────────────────────────────────────────────┘
```

### Flujo de una consulta del estudiante

```
  1. Usuario escribe pregunta + (opcional) sube imagen
                    │
                    ▼
  2. auth.py: Verifica sesión activa y bloqueos
                    │
                    ▼
  3. rag_search.py: Genera embedding de la pregunta
                    │
                    ▼
  4. Pinecone: Búsqueda semántica en namespace de materia
                    │
                    ▼
  5. ai_engine.py: Selecciona modelo según materia/contexto
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
  Grok (Sociales)      DeepSeek (Mates)      Gemini (Imagen)
         │                     │                     │
         └──────────┬──────────┴─────────────────────┘
                    ▼
  6. OpenRouter: Genera respuesta con método socrático
                    │
                    ▼
  7. database.py: Guarda conversación + descuenta créditos
                    │
                    ▼
  8. Streamlit: Muestra respuesta al usuario
                    │
                    ▼
  9. (Opcional) pdf_generator.py: Exporta conversación
```

### Módulos principales

| Módulo | Ubicación | Responsabilidad | Dependencias clave |
|--------|-----------|-----------------|-------------------|
| **Interfaz principal** | `app.py` | Orquestación del chat, gestión de sesión, UI | Streamlit, todos los módulos core/ |
| **Registro** | `pages/registro.py` | Formulario de alta (padre + estudiante + consentimiento) | Streamlit, core/database.py, core/auth.py |
| **Autenticación** | `core/auth.py` | Hashing y verificación de PIN con bcrypt | bcrypt, Supabase |
| **Base de datos** | `core/database.py` | CRUD de usuarios, chats, estudiantes, créditos | Supabase (cliente dual: normal + admin) |
| **RAG** | `core/rag_search.py` | Generación de embeddings y búsqueda vectorial | OpenAI, Pinecone |
| **Motor IA** | `core/ai_engine.py` | Selección de modelo LLM y construcción de prompts | OpenRouter, historial de conversación |
| **Exportación PDF** | `core/pdf_generator.py` | Conversión de chats a documentos PDF | FPDF2, limpieza de markdown/LaTeX |

### Decisiones de arquitectura clave

#### 1. Cliente dual de Supabase

El sistema utiliza dos instancias del cliente de Supabase:

- **Cliente normal** (`SUPABASE_KEY`): Para operaciones estándar respetando Row Level Security (RLS)
- **Cliente admin** (`SUPABASE_SERVICE_KEY`): Para operaciones administrativas que requieren bypass de RLS

Esto permite mantener la seguridad por defecto mientras se habilitan operaciones específicas como consultas globales o gestión de usuarios.

#### 2. Namespace por materia en Pinecone

Cada materia del ICFES tiene su propio namespace en el índice de Pinecone:
- `matematicas`
- `fisica`
- `sociales`
- `lectura_critica`
- `ingles`

Esto permite:
- Búsquedas más rápidas (índices especializados)
- Resultados más relevantes (sin contaminación entre materias)
- Escalabilidad independiente por materia

#### 3. Selección dinámica de modelo LLM

En lugar de usar un solo modelo para todo, `ai_engine.py` selecciona dinámicamente:

| Materia | Modelo | Razón |
|---------|--------|-------|
| Ciencias Sociales | Grok | Excelente en análisis crítico e interpretación contextual |
| Lectura Crítica | Grok | Capacidad superior para comprensión textual profunda |
| Matemáticas | DeepSeek | Optimizado para razonamiento lógico-formal |
| Física | DeepSeek | Precisión en cálculos y resolución de problemas |
| **Cualquiera + imagen** | Gemini | Único modelo con capacidad de visión multimodal |

#### 4. Sistema de créditos con RPC

Los créditos se gestionan mediante una función RPC en Supabase (`descontar_creditos`):

```sql
CREATE OR REPLACE FUNCTION descontar_creditos(
  user_email TEXT, 
  cantidad INTEGER
) RETURNS void AS $$
BEGIN
  UPDATE padres 
  SET creditos_totales = creditos_totales - cantidad 
  WHERE email = user_email;
END;
$$ LANGUAGE plpgsql;
```

Ventajas:
- **Atomicidad**: Garantiza que el descuento sea transaccional
- **Seguridad**: La lógica está en el servidor, no expuesta en el cliente
- **Auditoría**: Cambios rastreables en logs de Supabase

## 🛠️ Stack Tecnológico

### Lenguajes y frameworks

| Tecnología | Versión | Propósito | Documentación |
|-----------|---------|-----------|---------------|
| **Python** | 3.10+ | Lenguaje principal del backend | [python.org](https://www.python.org/) |
| **Streamlit** | 1.x | Framework web para la interfaz de usuario | [streamlit.io](https://streamlit.io/) |

### Servicios en la nube

| Servicio | Propósito | Características usadas |
|----------|-----------|------------------------|
| **Supabase** | Base de datos principal y autenticación | PostgreSQL, Row Level Security (RLS), funciones RPC |
| **Pinecone** | Almacenamiento y búsqueda de vectores | Índices especializados, namespaces, búsqueda semántica |
| **OpenRouter** | Gateway para múltiples modelos LLM | Grok, DeepSeek, Gemini (a través de API única) |
| **OpenAI** | Generación de embeddings | text-embedding-3-small (1536 dimensiones) |

### Bibliotecas principales

| Biblioteca | Versión recomendada | Uso |
|-----------|---------------------|-----|
| `streamlit` | ≥ 1.0 | Interfaz web reactiva |
| `supabase` | 2.x | Cliente Python para Supabase |
| `pinecone-client` | 3.x | Cliente Python para Pinecone |
| `openai` | 1.x | Generación de embeddings |
| `requests` | 2.x | Llamadas HTTP a OpenRouter |
| `bcrypt` | 4.x | Hashing seguro de PINs |
| `fpdf2` | 2.x | Generación de documentos PDF |
| `pytest` | 9.x | Framework de testing |
| `python-dotenv` | 1.x | Gestión de variables de entorno |

### Diagrama de dependencias

```
app.py
  ├── streamlit (UI)
  ├── core/auth.py
  │     └── bcrypt
  ├── core/database.py
  │     └── supabase
  ├── core/rag_search.py
  │     ├── openai (embeddings)
  │     └── pinecone
  ├── core/ai_engine.py
  │     ├── requests (OpenRouter)
  │     └── json
  └── core/pdf_generator.py
        └── fpdf2
```

### Requisitos del sistema

- **Sistema operativo**: Linux, macOS o Windows con WSL2
- **Python**: 3.10 o superior (recomendado: 3.12)
- **RAM**: Mínimo 2GB (recomendado: 4GB para desarrollo)
- **Conectividad**: Internet estable para APIs externas
- **Almacenamiento**: ~100MB para dependencias

---

## 🔧 Configuración e Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Idromerom714/Tutor-Icfes-AI.git
cd Tutor-Icfes-AI
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar secretos de Streamlit

Crear el archivo `.streamlit/secrets.toml` con las credenciales de los servicios:

```toml
# APIs de inteligencia artificial
OPENROUTER_API_KEY = "sk-or-v1-..."
OPENAI_API_KEY = "sk-proj-..."

# Pinecone (vector database)
PINECONE_API_KEY = "pcsk_..."
PINECONE_INDEX_NAME = "icfes-index"

# Supabase (base de datos principal)
SUPABASE_URL = "https://xxxxxxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Admin key
```

> ⚠️ **Importante**: Nunca commits este archivo al repositorio. Ya está incluido en `.gitignore`.

### 5. (Opcional) Configurar variables para scripts CLI

Algunos scripts en `scripts/` usan `.env` en lugar de `secrets.toml`:

```bash
# .env
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 6. Verificar instalación

```bash
streamlit run app.py
```

Debería abrir un navegador en `http://localhost:8501` con la interfaz de login.

---

## 📊 Estructura de Datos

### Modelo de base de datos en Supabase

El sistema utiliza un modelo relacional con 4 tablas principales:

#### Tabla: `padres`

Información de tutores legales o cuentas padre.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único (auto-generado) |
| `email` | TEXT | Email único del padre/tutor |
| `pin` | TEXT | Hash bcrypt del PIN de acceso |
| `nombre` | TEXT | Nombre completo del tutor |
| `plan` | TEXT | Tipo de plan: `basico`, `estandar`, `familia` |
| `estado` | TEXT | Estado de la cuenta: `activo`, `bloqueado`, `inactivo` |
| `creditos_totales` | INTEGER | Créditos disponibles para usar en sesiones |
| `intentos_fallidos` | INTEGER | Contador de intentos de login incorrectos |
| `fecha_creacion` | TIMESTAMP | Fecha de registro |

#### Tabla: `estudiantes`

Hijos o pupilos asociados a una cuenta padre.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `padre_id` | UUID | FK a `padres.id` |
| `nombre` | TEXT | Nombre del estudiante |
| `grado` | INTEGER | Grado escolar (6-11) |
| `fecha_registro` | TIMESTAMP | Fecha de alta |

#### Tabla: `historial_chats`

Registro de todas las conversaciones.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `email_usuario` | TEXT | Email del padre (FK implícita) |
| `estudiante_id` | UUID | FK a `estudiantes.id` |
| `titulo` | TEXT | Título auto-generado del chat |
| `materia` | TEXT | Matemáticas, Física, Sociales, etc. |
| `mensajes` | JSONB | Array de objetos `{role, content, timestamp}` |
| `fecha_creacion` | TIMESTAMP | Inicio de la conversación |
| `fecha_actualizacion` | TIMESTAMP | Última modificación |

#### Tabla: `consentimientos`

Registro de aceptación de políticas de privacidad (GDPR).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Identificador único |
| `padre_id` | UUID | FK a `padres.id` |
| `acepto_politica` | BOOLEAN | Aceptación explícita |
| `version_politica` | TEXT | Versión de la política aceptada (ej: `v1.0`) |
| `fecha_aceptacion` | TIMESTAMP | Momento de la aceptación |

### Funciones RPC requeridas

#### `descontar_creditos(user_email TEXT, cantidad INTEGER)`

Descuenta créditos atómicamente del saldo del padre.

**Implementación SQL:**

```sql
CREATE OR REPLACE FUNCTION descontar_creditos(
  user_email TEXT, 
  cantidad INTEGER
) RETURNS void AS $$
BEGIN
  UPDATE padres 
  SET creditos_totales = creditos_totales - cantidad 
  WHERE email = user_email AND creditos_totales >= cantidad;
  
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Créditos insuficientes o usuario no encontrado';
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

**Uso desde Python:**

```python
supabase.rpc('descontar_creditos', {
    'user_email': 'padre@example.com',
    'cantidad': 10
}).execute()
```

### Notas sobre el modelo legacy

⚠️ Algunos scripts antiguos (como `scripts/create_user.py`) utilizan una tabla llamada `perfiles` que ya no es el modelo principal de la aplicación. Se recomienda migrar esos scripts al modelo `padres/estudiantes`.

---

## 🚀 Uso y Ejecución

### Desarrollo local

```bash
streamlit run app.py
```

Esto iniciará la aplicación en `http://localhost:8501`.

### Desarrollo local

```bash
streamlit run app.py
```

### Producción (con configuraciones adicionales)

```bash
streamlit run app.py --server.enableCORS false --server.enableXsrfProtection false
```

> **Nota**: Las flags de CORS y XSRF se usan típicamente en entornos controlados. Para producción pública, evaluar implicaciones de seguridad.

---

## 📜 Scripts Disponibles

### `scripts/create_user.py`

Crea usuarios manualmente en Supabase.

**Características:**
- Modelo: usa tabla `perfiles` (legacy)
- Uso: requiere `.env` con `SUPABASE_URL` y `SUPABASE_KEY`
- Nota: considerar migrar a modelo `padres/estudiantes`

**Ejecución:**
```bash
python scripts/create_user.py
```

### `scripts/upload_pdfs.py`

Carga y vectoriza documentos PDF en Pinecone.

**Características:**
- Entorno: diseñado para Google Colab
- Funcionalidad: extrae texto, genera embeddings (OpenAI), inserta en Pinecone con namespaces por materia
- Limitación: depende de `google.colab`, no ejecutable localmente sin modificaciones

**Uso en Colab:**
1. Subir el script a Google Colab
2. Configurar las API keys en el entorno
3. Subir los PDFs de material ICFES
4. Ejecutar las celdas secuencialmente

### `scripts/publish_wiki.sh`

Publica la documentación wiki del proyecto.

**Ejecución:**
```bash
bash scripts/publish_wiki.sh
```

---

## 🧪 Pruebas

La suite de tests fue completamente renovada (marzo 2026) y está alineada con el código actual.

### Ejecutar tests

```bash
pytest          # Todos los tests
pytest -v       # Con detalle
pytest -q       # Modo silencioso
pytest tests/test_auth.py  # Módulo específico
```

### Estado actual

- ✅ **57 tests** (100% de éxito)
- 📁 **5 archivos**: `test_auth.py`, `test_database.py`, `test_rag_search.py`, `test_ai_engine.py`, `test_pdf_generator.py`
- 📋 **Cobertura**: todos los módulos `core/` (auth, database, RAG, AI engine, PDF generator)
- ⚙️ **Configuración**: `pytest.ini` + fixtures globales en `conftest.py`

### Resumen de módulos de prueba

| Módulo | Tests | Descripción |
|--------|-------|-------------|
| `test_auth.py` | 7 | Hashing y verificación de PINs con bcrypt |
| `test_database.py` | 10 | Operaciones CRUD en Supabase (usuarios, chats, créditos) |
| `test_rag_search.py` | 6 | Generación de embeddings y búsqueda en Pinecone |
| `test_ai_engine.py` | 15 | Selección de modelos, construcción de prompts, manejo de historial |
| `test_pdf_generator.py` | 19 | Exportación de chats a PDF, limpieza de markdown/LaTeX |

### Documentación

Ver [tests/README.md](tests/README.md) para detalles completos de cada módulo de pruebas.

---

## 🌐 Despliegue

### Streamlit Community Cloud (recomendado)

1. Conectar repositorio GitHub a Streamlit Cloud
2. Configurar secretos en el dashboard:
   - Copiar contenido de `.streamlit/secrets.toml`
   - Pegar en "Secrets" del proyecto
3. Especificar `app.py` como punto de entrada
4. Configurar Python 3.10+ como versión

### Otros entornos (Docker, VPS, etc.)

#### Docker (ejemplo básico)

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build y run:**
```bash
docker build -t tutor-icfes-ai .
docker run -p 8501:8501 tutor-icfes-ai
```

#### Consideraciones

- **Variables de entorno**: Asegurar que todas las API keys estén configuradas (especialmente `SUPABASE_SERVICE_KEY`)
- **Red**: Verificar conectividad a Supabase, Pinecone y OpenRouter
- **Puertos**: Streamlit usa puerto 8501 por defecto
- **Logs**: Configurar logging adecuado para monitoreo en producción
- **Seguridad**: Usar HTTPS en producción, configurar CORS apropiadamente

---

## ⚠️ Limitaciones Conocidas

1. **Scripts legacy**: `create_user.py` usa el modelo `perfiles` en lugar de `padres/estudiantes`
2. **Configuración dual**: `config.py` usa variables de entorno `.env`, pero la app principal usa `st.secrets`
3. **Upload de PDFs**: `scripts/upload_pdfs.py` depende de Google Colab (imports de `google.colab`)
4. **Costos de API**: El uso intensivo puede generar costos significativos en OpenRouter y OpenAI
5. **Latencia**: Las consultas RAG + LLM pueden tomar 3-10 segundos según la complejidad

---

## 📚 Wiki y Documentación

Documentación ampliada en `docs/wiki/`:

- [Home.md](docs/wiki/Home.md) - Introducción general al proyecto
- [Visión y Alcance](docs/wiki/Vision-y-alcance.md) - Objetivos y roadmap
- [Arquitectura y Flujo](docs/wiki/Arquitectura-y-flujo.md) - Diseño técnico detallado
- [Instalación y Configuración](docs/wiki/Instalacion-y-configuracion.md) - Guía paso a paso
- [Datos y Seguridad](docs/wiki/Datos-y-seguridad.md) - Modelo de datos, privacidad, GDPR
- [Operación y Monitoreo](docs/wiki/Operacion-y-monitoreo.md) - Mantenimiento y troubleshooting
- [FAQ](docs/wiki/FAQ.md) - Preguntas frecuentes

---

## 🗺️ Roadmap

### Alta prioridad

1. **🔧 Unificar modelo de datos**: Migrar scripts legacy de `perfiles` a `padres/estudiantes`
2. **⚙️ Centralizar configuración**: Consolidar `config.py` (.env) y `st.secrets` en una sola fuente
3. **📤 Adaptar upload de PDFs**: Convertir `scripts/upload_pdfs.py` para ejecución local sin Colab

### Media prioridad

4. **🧪 Tests de integración**: Agregar tests e2e con datos reales (marcados `@pytest.mark.integration`)
5. **📊  Cobertura de código**: Implementar medición con `pytest-cov` (objetivo: 80%+)
6. **📖 Documentación de API**: Generar docs automáticas con Sphinx o MkDocs

### Baja prioridad

7. **⚡ Optimización RAG**: Cache de embeddings frecuentes
8. **📈 Monitoreo**: Integrar telemetría (tiempos de respuesta, errores LLM)
9. **🔄 CI/CD**: Pipeline automatizado para tests y despliegue

---

## 📝 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

Asegúrate de que todos los tests pasen antes de enviar tu PR:
```bash
pytest -v
```

---

## 📧 Contacto

Para preguntas, sugerencias o reportes de bugs, por favor abre un [issue](https://github.com/Idromerom714/Tutor-Icfes-AI/issues) en GitHub.

---

**Última actualización**: Marzo 2026  
**Versión**: 1.0.0  
**Mantenido por**: [@Idromerom714](https://github.com/Idromerom714)
