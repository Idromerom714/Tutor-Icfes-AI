# Tutor-Icfes-AI
Tutor-Icfes-AI es un tutor conversacional para preparar el examen ICFES Saber 11. Combina chat educativo con RAG (búsqueda en documentos oficiales) y control de energía diaria por plan. La app está construida en Streamlit y se conecta a Supabase (usuarios), Pinecone (vectores) y modelos de IA vía OpenRouter/OpenAI.

## Contenido
- [Visión general](#visión-general)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Instalación local](#instalación-local)
- [Configuración de Secrets](#configuración-de-secrets)
- [Base de datos (Supabase)](#base-de-datos-supabase)
- [Carga de documentos](#carga-de-documentos)
- [Uso de la app](#uso-de-la-app)
- [Scripts](#scripts)
- [Pruebas](#pruebas)
- [Despliegue](#despliegue)
- [Guía del estudiante](#guía-del-estudiante)

## Visión general
- Chat con personalidad de "El Profe Saber" y enfoque socrático.
- RAG por materia: Matemáticas, Lectura Crítica, Sociales, Ciencias Naturales e Inglés.
- **Sistema de energía con recarga diaria automática** por plan (básico y avanzado).
- Soporte para imágenes (fotos de preguntas) con análisis visual.

## Sistema de Energía (Créditos)
La aplicación usa un sistema de "energía" (créditos) que se **recarga automáticamente cada día**:

### Planes Disponibles:
- **Plan Básico**: 50⚡ diarios
- **Plan Avanzado**: 150⚡ diarios

### Costos por Operación:
- **Pregunta simple** (texto): 1⚡
- **Pregunta de análisis crítico** (Sociales/Lectura Crítica): 8⚡
- **Pregunta con imagen**: +5⚡ adicionales

### Recarga Automática:
- La energía se recarga **automáticamente** cada día a las 00:00 (hora de Colombia)
- Los créditos se **acumulan** si no se gastan (no se pierden)
- El sistema verifica la fecha al iniciar sesión
- Se muestra una notificación cuando hay recarga diaria

## Arquitectura
Flujo principal de una consulta:
1. El estudiante se autentica por correo + PIN.
2. Se selecciona una materia, que mapea al `namespace` de Pinecone.
3. Se genera un embedding con OpenAI y se consulta Pinecone (top 3).
4. Se arma el prompt con el contexto y la pregunta.
5. Se llama al modelo vía OpenRouter.
6. Se responde y se descuentan créditos en Supabase.

Componentes clave:
- [app.py](app.py): UI y flujo principal en Streamlit.
- [core/ai_engine.py](core/ai_engine.py): Llamadas a OpenRouter y manejo de imágenes.
- [core/rag_search.py](core/rag_search.py): Embeddings + consulta Pinecone.
- [core/database.py](core/database.py): Lectura y actualización de usuarios en Supabase.
- [scripts/](scripts/): utilidades de administración.

## Requisitos
- Python 3.10+
- Cuenta y llaves para:
	- Supabase (DB de usuarios)
	- Pinecone (índice vectorial)
	- OpenAI (embeddings)
	- OpenRouter (modelo de chat)

Dependencias en [requirements.txt](requirements.txt).

## Instalación local
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración de Secrets
La app usa `st.secrets`. Crea el archivo `.streamlit/secrets.toml`:

```toml
OPENROUTER_API_KEY = "..."
OPENAI_API_KEY = "..."
PINECONE_API_KEY = "..."
PINECONE_INDEX_NAME = "icfes-index"
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "..."
```

Notas:
- `PINECONE_INDEX_NAME` debe existir y tener namespaces por materia en minúscula.
- El modelo de chat se define en [core/ai_engine.py](core/ai_engine.py#L11).

## Base de datos (Supabase)
Se espera una tabla `perfiles` con al menos estas columnas:

| Columna | Tipo | Descripción |
| --- | --- | --- |
| email | text (PK) | Identificador del estudiante |
| pin | text/int | PIN de acceso (4 dígitos) |
| plan | text | `basico` o `avanzado` |
| creditos_totales | int | Saldo actual de energía/créditos |
| ultima_fecha | date | Fecha de la última recarga |

### Lógica de Recarga Diaria:
La función `verificar_y_recargar_creditos()` en [core/database.py](core/database.py):
1. Compara `ultima_fecha` con la fecha actual
2. Si es un nuevo día, agrega los créditos del plan a `creditos_totales`
3. Actualiza `ultima_fecha` con la fecha actual
4. Se ejecuta automáticamente al obtener datos del usuario

## Carga de documentos
El repositorio incluye [scripts/upload_pdfs.py](scripts/upload_pdfs.py), actualmente vacío. Se sugiere implementar un flujo que:
1. Lea PDFs (PyPDF2).
2. Trocee el texto por páginas o chunks.
3. Genere embeddings con OpenAI.
4. Inserte en Pinecone con `namespace` por materia.

## Uso de la app
```bash
streamlit run app.py --server.enableCORS false --server.enableXsrfProtection false
```

## Scripts
- [scripts/create_user.py](scripts/create_user.py): crea un estudiante en Supabase. Usa `.env`.

Archivo `.env` requerido para scripts:
```env
SUPABASE_URL=...
SUPABASE_KEY=...
```

## Pruebas
```bash
pytest
```

## Despliegue
Recomendado: Streamlit Community Cloud.
- Configura los mismos secretos que en `.streamlit/secrets.toml`.
- Asegura conectividad a Supabase, Pinecone y OpenRouter.

## Guía del estudiante
### Energia diaria
- Plan basico: 10 preguntas y 5 fotos.
- Plan avanzado: 50 preguntas y 12 fotos.
- La energia no es acumulable.

### Buenas practicas para fotos
- Texto nítido y centrado.
- Buena luz, sin sombras.
- Incluye graficas o mapas si hacen parte de la pregunta.

### Como preguntar
- Evita: "Dame la respuesta".
- Prefiere: "No entiendo por que se descarta la opcion C".
- Ideal: "Explicame el concepto y dame pistas".

### Consejo del Profe
El ICFES mide comprension lectora y pensamiento critico. Usa tus preguntas diarias para entender el por que.


### 📖 Guía del Estudiante

¡A romperla con el Profe Saber! ¡Hola, futuro universitario! Si tienes este manual, es porque ya diste el primer paso para asegurar ese cupo en la UdeA, la Nacho o la universidad de tus sueños. Yo soy El Profe Saber, tu tutor personal de IA, y aquí te enseñaré cómo sacarme el máximo provecho.

⚡ 1. Tu Energía Diaria: Úsala con Sabiduría Para que tu preparación sea constante (y no dejes todo para el último día), tienes una cuota de "Energía" que se recarga cada mañana:

Plan Básico: 10 preguntas y 5 fotos al día.

Plan Avanzado: 50 preguntas y 12 fotos al día.

Ojo: La energía no es acumulable. Si hoy no usas tus 10 preguntas, mañana no tendrás 20; ¡así que entra a diario y practica al menos un poco!

📸 2. Cómo tomar fotos "Pro" para la IA Si vas a subir una foto de un simulacro físico o de tu cuaderno, sigue estos consejos para que no pierdas tus créditos por una imagen borrosa:

Enfoca bien: Asegúrate de que el texto de la pregunta se lea claramente.

Buena luz: Evita las sombras de tu mano o del celular sobre el papel.

Céntrate en la duda: Intenta que en la foto solo salga la pregunta que te interesa y sus opciones (A, B, C, D).

Gráficas: Si la pregunta tiene un mapa o una gráfica, ¡inclúyela! Yo puedo analizar datos visuales.

🗣️ 3. Cómo preguntarme (El arte de aprender) Recuerda que yo no soy una máquina de dar respuestas, soy tu entrenador. Si solo me pides "la respuesta de la 5", te daré una pista para que tú la encuentres.

Mal: "¿Cuál es la respuesta de esta pregunta?"

Bien: "Profe, no entiendo por qué en esta pregunta de Sociales se descarta la opción C. ¿Me explica el concepto?"

Mejor: "Profe, explíqueme la Ley de Newton aplicada a este problema de la foto."

🧠 4. Los Secretos de la Biblioteca Tengo acceso a una Biblioteca Virtual con miles de páginas de documentos oficiales del ICFES. Cuando te responda, muchas veces te diré: "Según los estándares de Lectura Crítica...". Eso significa que la información es 100% confiable y basada en cómo evalúan realmente en Colombia.

🛠️ 5. Soporte y Ayuda Si tienes problemas con tu PIN de acceso o sientes que tu energía no se recargó:

Escríbenos al WhatsApp: [Tu número de soporte aquí]

Horario: Lunes a Viernes de 8:00 AM a 6:00 PM.

🚀 ¡El consejo del Profe! El ICFES no solo mide qué tanto sabes, sino qué tan bien lees. No te satures. Usa tus preguntas diarias para entender el porqué de las cosas, no para memorizar.

¡Vamos por ese puntaje de 400+! Nos vemos en el chat.