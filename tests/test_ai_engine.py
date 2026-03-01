"""
Tests para el motor de IA (core/ai_engine.py).
"""

import pytest
from unittest.mock import patch, MagicMock


class TestSeleccionModelo:
    """Tests para la lógica de selección de modelos según materia"""

    @patch("core.ai_engine.requests.post")
    def test_sociales_usa_grok(self, mock_post):
        """Sociales debe usar Grok para análisis crítico"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Respuesta de Grok"}}]
        }

        llamar_profe_saber(
            mensaje_usuario="¿Qué fue la Revolución Francesa?",
            contexto_pdf="Contexto histórico...",
            imagen_bytes=None,
            materia="Sociales",
            historial_mensajes=[]
        )

        payload = mock_post.call_args[1]["json"]
        assert "grok" in payload["model"].lower()

    @patch("core.ai_engine.requests.post")
    def test_lectura_critica_usa_grok(self, mock_post):
        """Lectura Crítica debe usar Grok"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Análisis crítico"}}]
        }

        llamar_profe_saber(
            mensaje_usuario="Analiza este texto",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Lectura Crítica",
            historial_mensajes=[]
        )

        payload = mock_post.call_args[1]["json"]
        assert "grok" in payload["model"].lower()

    @patch("core.ai_engine.requests.post")
    def test_matematicas_con_imagen_usa_gemini(self, mock_post):
        """Matemáticas con imagen debe usar Gemini (visión mejorada)"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Análisis visual"}}]
        }

        llamar_profe_saber(
            mensaje_usuario="Resuelve este problema",
            contexto_pdf="",
            imagen_bytes=b"fake_image_data",
            materia="Matemáticas",
            historial_mensajes=[]
        )

        payload = mock_post.call_args[1]["json"]
        model = payload["model"].lower()
        assert "gemini" in model or "google" in model

    @patch("core.ai_engine.requests.post")
    def test_matematicas_sin_imagen_usa_deepseek(self, mock_post):
        """Matemáticas sin imagen debe usar DeepSeek (lógica pura)"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Solución lógica"}}]
        }

        llamar_profe_saber(
            mensaje_usuario="¿Cuánto es 2 + 2?",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Matemáticas",
            historial_mensajes=[]
        )

        payload = mock_post.call_args[1]["json"]
        assert "deepseek" in payload["model"].lower()

    @patch("core.ai_engine.requests.post")
    def test_fisica_con_imagen_usa_gemini(self, mock_post):
        """Física con imagen debe usar Gemini"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Análisis de diagrama"}}]
        }

        llamar_profe_saber(
            mensaje_usuario="Explica este diagrama",
            contexto_pdf="",
            imagen_bytes=b"diagram_data",
            materia="Física",
            historial_mensajes=[]
        )

        payload = mock_post.call_args[1]["json"]
        model = payload["model"].lower()
        assert "gemini" in model or "google" in model


class TestPromptSocratico:
    """Tests para el prompt del método socrático"""

    def test_prompt_existe_y_tiene_contenido(self):
        """El prompt debe estar definido y tener contenido significativo"""
        from core.ai_engine import PROFE_SABER_PROMPT

        assert PROFE_SABER_PROMPT is not None
        assert len(PROFE_SABER_PROMPT) > 500  # Debe ser un prompt robusto

    def test_prompt_menciona_metodo_socratico(self):
        """Debe mencionar el método socrático o hacer preguntas"""
        from core.ai_engine import PROFE_SABER_PROMPT

        prompt_lower = PROFE_SABER_PROMPT.lower()
        assert "socr" in prompt_lower or "pregunta" in prompt_lower

    def test_prompt_instrucciones_anti_respuesta_directa(self):
        """Debe instruir a NO dar respuestas directas"""
        from core.ai_engine import PROFE_SABER_PROMPT

        prompt_lower = PROFE_SABER_PROMPT.lower()
        # Buscar palabras clave que indiquen restricción
        assert any(keyword in prompt_lower for keyword in ["nunca", "no digas", "evita", "prohib"])

    def test_prompt_menciona_identidad_profe_saber(self):
        """Debe establecer la identidad 'El Profe Saber'"""
        from core.ai_engine import PROFE_SABER_PROMPT

        assert "profe saber" in PROFE_SABER_PROMPT.lower()


class TestManejoHistorial:
    """Tests para el manejo del historial de conversación"""

    @patch("core.ai_engine.requests.post")
    def test_historial_incluido_en_mensajes(self, mock_post):
        """El historial debe incluirse en los mensajes al LLM"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Respuesta contextual"}}]
        }

        historial = [
            {"role": "user", "content": "Primera pregunta"},
            {"role": "assistant", "content": "Primera respuesta"}
        ]

        llamar_profe_saber(
            mensaje_usuario="Segunda pregunta",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Matemáticas",
            historial_mensajes=historial
        )

        payload = mock_post.call_args[1]["json"]
        mensajes = payload["messages"]

        # Debe tener: 1 system + 2 historial + 1 actual
        assert len(mensajes) >= 3
        
        # Verificar que el historial esté presente
        contenidos = [m.get("content") for m in mensajes if isinstance(m.get("content"), str)]
        assert any("Primera pregunta" in c for c in contenidos)

    @patch("core.ai_engine.requests.post")
    def test_funciona_sin_historial(self, mock_post):
        """Debe funcionar correctamente con historial vacío"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Primera respuesta"}}]
        }

        respuesta = llamar_profe_saber(
            mensaje_usuario="Primera pregunta del chat",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Matemáticas",
            historial_mensajes=[]
        )

        assert respuesta is not None
        assert "Primera respuesta" in respuesta


class TestManejoErrores:
    """Tests para el manejo de errores"""

    @patch("core.ai_engine.requests.post")
    def test_error_api_retorna_mensaje(self, mock_post):
        """Debe retornar mensaje de error amigable si falla la API"""
        from core.ai_engine import llamar_profe_saber

        mock_post.return_value.json.return_value = {
            "error": {"message": "Rate limit exceeded"}
        }

        respuesta = llamar_profe_saber(
            mensaje_usuario="Test",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Matemáticas",
            historial_mensajes=[]
        )

        assert "⚠️" in respuesta or "problema" in respuesta.lower()

    @patch("core.ai_engine.requests.post")
    def test_excepcion_red_manejada(self, mock_post):
        """Debe manejar excepciones de red"""
        from core.ai_engine import llamar_profe_saber

        mock_post.side_effect = Exception("Connection timeout")

        respuesta = llamar_profe_saber(
            mensaje_usuario="Test",
            contexto_pdf="",
            imagen_bytes=None,
            materia="Matemáticas",
            historial_mensajes=[]
        )

        assert "❌" in respuesta or "error" in respuesta.lower()


class TestGenerarTituloChat:
    """Tests para generar_titulo_chat"""

    @patch("core.ai_engine.requests.post")
    def test_genera_titulo_corto(self, mock_post):
        """Debe generar un título corto para el chat"""
        from core.ai_engine import generar_titulo_chat

        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Teorema de Pitágoras"}}]
        }

        titulo = generar_titulo_chat("¿Qué es el teorema de Pitágoras y cómo se aplica?")

        assert titulo is not None
        assert len(titulo) > 0
        assert len(titulo) < 100  # Debe ser título corto

    @patch("core.ai_engine.requests.post")
    def test_titulo_fallback_en_error(self, mock_post):
        """Debe retornar un título fallback si hay error"""
        from core.ai_engine import generar_titulo_chat

        mock_post.side_effect = Exception("API Error")

        titulo = generar_titulo_chat("Pregunta de matemáticas complicada")

        assert titulo is not None
        assert "Consulta" in titulo or "Pregunta" in titulo.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
